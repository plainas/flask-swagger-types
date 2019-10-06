from flask import Flask, request, make_response, Response
import marshmallow
import pkg_resources
from flaskswaggertypes import FlaskSwaggerTypes

# 1. Define some general details of you want included in your spec.
spec_metadata = {
    'title': "My fancy web api",
    'description': "Does some fancy api stuff on my fancy api-y server" ,
    #'basePath': "/sofancy/",
    'version': "33",
    #'host': "fancy.example.com"
}


# 2. Define some marshmallow schemas 
class Pants(marshmallow.Schema):
    _id = marshmallow.fields.Int()
    name = marshmallow.fields.String()
    brand = marshmallow.fields.String() 
    size = marshmallow.fields.Int()
    
class PantsList(marshmallow.Schema):
    pants = marshmallow.fields.Nested(Pants, many=True)

# 3. Create your flask app as usual
app = Flask(__name__)

# 4. Initialize flask-swagger-types
fst = FlaskSwaggerTypes(app, spec_metadata)

responses = [
    [ 200 , "Server will reply with 200 to successfull calls" ],
    [ 400 , "Just mentioning that calls to this api method could go south"],
]


# 5. Define some routes with @Fstroute()
@fst.Fstroute('/savePants', "POST", {'body' : Pants }, responses)
def saveYourFancyPants():
    # Parsed and validated data will be available at
    print(request.fst_data)
    #...
    return "Success!!!"


# parth paramters are parsed and will automatically show up in your swagger spec 
# without the need to manually pass its schema. 
@fst.Fstroute('/getManyPants/<int:size>/<string:brand>', "GET", {}, responses )
def getManyFancyPants(size, brand):
    print(request.fst_data)
    # ...
    return "your pants list here"


# you can optionally pass the response Schema
responses = [
    [ 200 , "Server will reply with 200 to successfull calls", PantsList ],
    [ 400 , "Server will repply with 400 if it rails to retrieve a list of pants" ],
]


@fst.Fstroute('/getManyPants', "GET", {}, responses)
def getFancyPants():
    pantslistschema = PantsList()
    empty_list = pantslistschema.dumps([])
    return empty_list


# 6. Start your flask app as usual
app.run()