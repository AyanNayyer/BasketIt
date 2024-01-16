from flask import Flask
from applications.database import db
from flask_cors import CORS
from flask_restful import Api
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "secret"

    db.init_app(app)

    app.app_context().push()

    return app

app = create_app()

from applications.controllers import *
from applications.api import SectionsResource,ProductsResource,AdditionalSectionsResource,AdditionalProductsResource,Sectionpost,Productspost
api=Api(app)
app.app_context().push()
api.add_resource(SectionsResource, '/api/sections/<int:id>')
api.add_resource(Sectionpost, '/api/sections/post')
api.add_resource(ProductsResource, '/api/products/<int:id>')
api.add_resource(Productspost, '/api/products/post')
api.add_resource(AdditionalSectionsResource, '/api/sections/display')
api.add_resource(AdditionalProductsResource, '/api/products/display')

if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", port=2345, debug=True)
