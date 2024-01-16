from flask import jsonify,abort
from flask_restful import Resource, reqparse
from applications.models import Section,Product
from applications.database import *
from datetime import datetime

class SectionsResource(Resource):
    def get(self, id=None):
        if id is not None:
            section = Section.query.get(id)
            if not section:
                return jsonify({"message": "Section not found."}), abort(404)
            return jsonify({"id": section.id, "name": section.name})

    def put(self, id=None):
        if id is None:
            return jsonify({"message": "Section ID is missing."}), 400

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Name field is required.")
        args = parser.parse_args()

        section = Section.query.get(id)
        if not section:
            return jsonify({"message": "Section not found."}), abort(404)

        section.name = args['name']
        db.session.commit()
        return jsonify({"message": "Section updated successfully."})

    def delete(self, id=None):
        if id is None:
            return jsonify({"message": "Section ID is missing."}), 400

        section = Section.query.get(id)
        if not section:
            return jsonify({"message": "Section not found."}), abort(404)

        db.session.delete(section)
        db.session.commit()
        return jsonify({"message": "Section deleted successfully."})
    
class Sectionpost(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Name field is required.")
        args = parser.parse_args()

        new_section = Section(name=args['name'])
        db.session.add(new_section)
        db.session.commit()
        return ({"message": "Section added successfully."}), 200

class ProductsResource(Resource):
    def get(self, id=None):
        if id is not None:
            products = Product.query.get(id)
            if not products:
                return jsonify({"message": "Product not found."}), abort(404)
            return jsonify({"id": products.id, "name": products.name, "manufacture_date": products.manufacture_date,
                          "expiry_date": products.expiry_date, "rate": products.rate, "stock": products.stock,
                          "owner": products.owner, "section_id": products.section_id})

    def _parse_product_arguments(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Name field is required.")
        parser.add_argument('manufacture_date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'), help="Invalid manufacture_date format. Please use 'YYYY-MM-DD'.")
        parser.add_argument('expiry_date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'), help="Invalid expiry_date format. Please use 'YYYY-MM-DD'.")
        parser.add_argument('rate', type=float)
        parser.add_argument('stock', type=int, required=True, help="Stock field is required.")
        parser.add_argument('owner', type=int, required=True, help="Owner field is required.")
        parser.add_argument('section_id', type=int, required=True, help="Section ID field is required.")
        return parser.parse_args()


    def put(self, id):
        args = self._parse_product_arguments()

        product = Product.query.get(id)
        if not product:
            return jsonify({"message": "Product not found."}), abort(404)

        product.name = args['name']
        product.manufacture_date = args['manufacture_date']
        product.expiry_date = args['expiry_date']
        product.rate = args['rate']
        product.stock = args['stock']
        product.owner = args['owner']
        product.section_id = args['section_id']
        db.session.commit()
        return jsonify({"message": "Product updated successfully."})

    def delete(self, id):
        product = Product.query.get(id)
        if not product:
            return jsonify({"message": "Product not found."}), abort(404)

        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully."})

class Productspost(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help="Name field is required.")
        parser.add_argument('manufacture_date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'), help="Invalid manufacture_date format. Please use 'YYYY-MM-DD'.")
        parser.add_argument('expiry_date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'), help="Invalid expiry_date format. Please use 'YYYY-MM-DD'.")
        parser.add_argument('rate', type=float)
        parser.add_argument('stock', type=int, required=True, help="Stock field is required.")
        parser.add_argument('owner', type=int, required=True, help="Owner field is required.")
        parser.add_argument('section_id', type=int, required=True, help="Section ID field is required.")
        args = parser.parse_args()

        new_product = Product(name=args['name'], manufacture_date=args['manufacture_date'],
                              expiry_date=args['expiry_date'], rate=args['rate'], stock=args['stock'],
                              owner=args['owner'], section_id=args['section_id'])
        db.session.add(new_product)
        db.session.commit()
        return ({"message": "Product added successfully."}), 201
    

class AdditionalSectionsResource(Resource):
    def get(self):
        sections = Section.query.all()
        sections_list = [{"id": section.id, "name": section.name} for section in sections]
        return jsonify(sections_list)

class AdditionalProductsResource(Resource):
    def get(self):
        products = Product.query.all()
        products_list = [{"id": product.id, "name": product.name, "manufacture_date": product.manufacture_date,
                          "expiry_date": product.expiry_date, "rate": product.rate, "stock": product.stock,
                          "owner": product.owner, "section_id": product.section_id} for product in products]
        return jsonify(products_list)