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
SAMPLE_APP_PLACEHOLDER
```

## Api reference
    #TODO.
    The sample app should cover what you need. If not, read the source. It's less than 200 lines of code.