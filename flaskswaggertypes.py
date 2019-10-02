from flask import Flask, request, make_response, Response
import simplejson
import marshmallow
from collections import namedtuple

from apispec.ext.marshmallow.swagger import fields2jsonschema, schema2jsonschema, schema2parameters, fields2parameters
from werkzeug.routing import parse_rule as werkzeurg_parse_rule


# NOT YET implemented:
#   * Tags

# Not supported by design
#   * OpenApi v3 (currently only version 2.0 is supported)
#   * Fine grain security (this will suport global security definitions only)


class FlaskSwaggerTypes:
    
    SpecMetadata = namedtuple('SpecMetadata', 'title description basePath version host securityDefinitions')
    SpecMetadata.__new__.__defaults__ = (None,) * len(SpecMetadata._fields)

    def __init__(self, flask_app, spec_metadata={}):
        self.flask_app = flask_app
        self.swagger_endpoints = dict()
        self.swagger_definition_schemas = []
        self.swagger_metadata = self.SpecMetadata(**spec_metadata)
        self.flask_app.add_url_rule("/swagger_spec", "getSwaggerSpec" , self.getSwaggerSpec)
        
    def getSwaggerSpec(self):
            spec_text = self.generate_swagger_spec()
            resp = Response(spec_text)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

    def _extract_path_schema_from_werkzeug_rule(self, rule, schema_name_prefix):
        parsed_rule_gen = werkzeurg_parse_rule(rule)
        path_params = [ path_fragment for path_fragment in parsed_rule_gen if path_fragment[0] is not None ]

        types_map = {
            'default'   : marshmallow.fields.String,
            'string'    : marshmallow.fields.String,
            'int'       : marshmallow.fields.Integer
        }

        schema_fields = {}
        for path_param in path_params:
            #Customize the error message a little bit to make it more obvious, this would raise KeyError anyway
            if path_param[0] not in types_map:
                raise KeyError("Unknonwn path parameter type: '" + str(path_param[0]) + "'. Flask-swagger-types only suports 'int' and 'string' types in path")            
            schema_fields[path_param[2]] = types_map[path_param[0]](required=True)

        PathSchema = type( schema_name_prefix + 'PathSchema', (marshmallow.Schema,), schema_fields)
        return PathSchema


    def _append_swagger_endpoint(self, rule, method, function_name, schemas, responses):
        
        swagger_formated_rule = "".join([ path_fragment[2] if path_fragment[0] is None else '{' + path_fragment[2] + '}' for path_fragment in werkzeurg_parse_rule(rule) ])
        
        val = {
            'method': method.lower(),
            'schemas': schemas,
            'responses': responses,
            'function_name' : function_name
        }

        if swagger_formated_rule in self.swagger_endpoints:
            self.swagger_endpoints[swagger_formated_rule].append(val)
        else:
            self.swagger_endpoints[swagger_formated_rule] = [val]

        if 'body' in schemas:
            self.swagger_definition_schemas.append(schemas['body'])

        # Duplicates are fine, this is uniquified later anyway as the class name is going to be used as a dict key
        [ self.swagger_definition_schemas.append(response_schema[2]) for response_schema in responses if len(response_schema) > 2 ]
            

    def _generate_swagger_definitions_tree(self):
        definitions = {}
        for schema in self.swagger_definition_schemas:
            definitions[schema.__name__] = schema2parameters(schema)[0]['schema']
        return definitions


    def _response2swagger_response_node(self, response):
        swagger_response_node = {}
        swagger_response_node['description'] = response[1]
        if len(response) > 2:
            swagger_response_node['schema'] = {}
            swagger_response_node['schema']['$ref'] = "#/definitions/" + response[2].__name__
        return swagger_response_node


    def _endpoint_schemas2swagger_parameters(self, endpoint_schemas):
        parameters = []
        if 'path' in endpoint_schemas:
            parameters += schema2parameters(endpoint_schemas['path'], default_in="path")

        if 'query' in endpoint_schemas:
            parameters += schema2parameters(endpoint_schemas['query'], default_in="query") 

        if 'header' in endpoint_schemas:
            parameters += schema2parameters(endpoint_schemas['header'], default_in="header")

        if 'body' in endpoint_schemas:            
            parameters += [{
                'in' : 'body',
                'name': 'body',
                'required': True,
                'schema' : {'$ref': "#/definitions/" + endpoint_schemas['body'].__name__ }
            }]

        return parameters


    def _endpoint2swagger_endpoint(self, endpoint):
        swagger_path_node = {
            'operationId' : endpoint['function_name'],
            'responses' : { response[0] : self._response2swagger_response_node(response) for response in endpoint['responses'] },
            'parameters' : self._endpoint_schemas2swagger_parameters(endpoint['schemas'])
        }                
        return swagger_path_node


    def _generate_swagger_paths_tree(self):
        paths_tree = {}
        for path in self.swagger_endpoints:
            paths_tree[path] = { endpoint['method'] : self._endpoint2swagger_endpoint(endpoint) for endpoint in self.swagger_endpoints[path] }
        return paths_tree


    def generate_swagger_spec(self):
        info = {
            'description' : self.swagger_metadata.description,
            'version': self.swagger_metadata.version,
            'title': self.swagger_metadata.title
        }

        swagger_spec_tree ={
            'swagger': "2.0",
            'info': info,
            'host': self.swagger_metadata.host,
            'basePath': self.swagger_metadata.basePath,
            'paths': self._generate_swagger_paths_tree(),
            'definitions': self._generate_swagger_definitions_tree(),
            'securityDefinitions' : self.swagger_metadata.securityDefinitions
        }

        swagger_spec_tree_without_empty_fields = {k: v for k, v in swagger_spec_tree.items() if v}

        return simplejson.dumps(swagger_spec_tree_without_empty_fields, indent=4)


    def _validate_input_data_with_schemas(self, request, input_schemas):
        fsa_data = {}

        errors = []
        if 'body' in input_schemas:
            fsa_data['body'], errors = input_schemas['body']().load(request.get_json())
            if errors:
                return fsa_data, errors

        if 'query' in input_schemas:
            # request.args is a multidict, let's use the good old dict interface for simplicity
            # we are not intersted in corner cases such as passing multiple values in the same key
            # read more here:
            #  http://werkzeug.pocoo.org/docs/0.12/datastructures/#werkzeug.datastructures.MultiDict
            fsa_data['query'], errors = input_schemas['query']().load(request.args)
            if errors:
                return fsa_data, errors

        if 'path' in input_schemas:
            # at this point, flask already validate this, so we can proceed with confidence
            fsa_data['path'] = input_schemas['path']().load(request.view_args)
        
        if 'header' in input_schemas:
            fsa_data['header'], errors = input_schemas['header']().load(request.headers)
        
        return fsa_data, errors
        


    def Fstroute(self,rule, http_verb, input_schemas={}, responses={}, **options):
        # we allow only one method per route and there is no default
        # this is diferent than flask's philosopy which provides many defaults
        if http_verb not in ["GET", "POST", "PUT", "DELETE"]:
            exit("invalid method" + str(http_verb))

        def decorator(f):
            input_schemas['path'] = self._extract_path_schema_from_werkzeug_rule(rule, f.__name__)
            self._append_swagger_endpoint(rule, http_verb, f.__name__, input_schemas, responses)    

            def modified_f(*a, **kw):
                validatedData, errors = self._validate_input_data_with_schemas(request, input_schemas)
                if errors:
                    error_message = simplejson.dumps(errors)
                    return make_response(error_message, 400)

                request.fst_data = validatedData
                return f(*a,**kw)

            self.flask_app.add_url_rule(rule, f.__name__ , modified_f , methods=[http_verb], **options)
            return f
        return decorator

