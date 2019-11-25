# Flask-swagger-types

Flask-swagger-types is a [swagger](https://swagger.io/) spec generator and type checker for flask applications. Define [marshmallow](https://marshmallow.readthedocs.io/en/stable/index.html) schemas for your input data and responses, anotate your routes with `@FlaskSwaggerTypes.Fstroute()` using these schemas, and get a swagger spec free at `[YOUR_APP_URL]/swagger_spec`.

Swagger_ui is exposed for convenience at `[YOUR_APP_URL]/swagger_ui`.

No hand written swagger spec chunks or monster docstrings non-sense. Your swagger spec is generated from your application semantics. Why wouldn't it, really?

`@FlaskSwaggerTypes.Fstroute()` calls flask's own `@flask.route()` under the hood, so all of Flask's funcionality is preserved and you can mix both anotations in the same application. This is usefull if you want to expose only a subset of your application rules in your swagger spec.

Flask-swagger-types is **not** a flask plugin. It is just a tiny helper with a single anotation definition.

# Installation

```bash
pip3 install https://github.com/plainas/flask-swagger-types/zipball/master
```

# Example app:

```python
from flask import Flask, request, make_response, Response
import marshmallow
import pkg_resources
from flaskswaggertypes import FlaskSwaggerTypes

# 1. Define some general info you want included in your spec.
spec_metadata = {
    'title': "My fancy web api",
    'description': "Does some fancy api stuff on my fancy api-y server" ,
    #'basePath': "/sofancy/", #(optional)
    'version': "33",
    #'host': "fancy.example.com" #(optional)
}


# 2. Define some marshmallow schemas 
class Pants(marshmallow.Schema):
    _id = marshmallow.fields.Int()
    name = marshmallow.fields.String()
    brand = marshmallow.fields.String() 
    size = marshmallow.fields.Int()
    
# You can define collections by nesting an existing type with Nested()
class PantsList(marshmallow.Schema):
    pants = marshmallow.fields.Nested(Pants, many=True)


# responses are defined like so:
responses = [
    [ 200 , "Server will reply with 200 to successfull calls" ],
    [ 400 , "Just mentioning that calls to this api method could go south"],
]

# you can optionally pass the response Schema
responses_with_type = [
    [ 200 , "Server will reply with 200 to successfull calls", PantsList ],
    [ 400 , "Server will repply with 400 if it rails to retrieve a list of pants" ],
]


# 3. Create your flask app as usual
app = Flask(__name__)

# 4. Initialize flask-swagger-types
fst = FlaskSwaggerTypes(app, spec_metadata)

# 5. Define some routes with @Fstroute()
@fst.Fstroute('/savePants', "POST", {'body' : Pants }, responses)
def saveYourFancyPants():
    # Parsed and validated data will be available at
    print(request.fst_data)
    #...
    return "Success!!!"


# path paramters are parsed and will automatically show up in your swagger spec 
# without the need to manually pass its schema. 
@fst.Fstroute('/getManyPants/<int:size>/<string:brand>', "GET", {}, responses )
def getManyFancyPants(size, brand):
    print(request.fst_data)
    # ...
    return "your pants list here"


@fst.Fstroute('/getFancyPants', "GET", {}, responses_with_type)
def getFancyPants():
    pantslistschema = PantsList()
    empty_list = pantslistschema.dumps([])
    return empty_list


# 6. Start your flask app as usual
app.run()
# Your swagger spec can now be accessed at [YOUR_APP_URL]/swagger_spec
# To browse your api with swager-ui, go to [YOUR_APP_URL]/swagger_ui?url=/swagger_spec#/default
```

## Api reference
    #TODO.
    The sample app should cover what you need. If not, read the source. It's less than 200 lines of code.
