#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return make_response([restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in restaurants], 200)

class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return make_response(restaurant.to_dict(), 200)
        else:
            return make_response({"error": "Restaurant not found"}, 404)
    
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response('', 204)
        else:
            return make_response({"error": "Restaurant not found"}, 404)

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return make_response([pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas], 200)

class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            return make_response(restaurant_pizza.to_dict(), 201)
        except ValueError as e:
            db.session.rollback()
            return make_response({"errors": ["validation errors"]}, 400)
        except Exception as e:
            db.session.rollback()
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)