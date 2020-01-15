from setuptools import setup

setup(name='flaskswaggertypes',
      version='0.2',
      description='A swagger spec generator and type checker for flask',
      url='https://github.com/plainas/flask-swagger-types',
      author='Pedro',
      author_email='pedroghcode@gmail.com',
      platforms='any',
      zip_safe=False,
      install_requires=[
            'apispec==0.27.0',
            'marshmallow==2.15.1',
            'Flask==1.1.1',
      ],
      package_dir={
            'fstdata':'data'
      },
      package_data={
            'fstdata': ['swagger.html'],
      },
      include_package_data=True,
)
