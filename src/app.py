"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200

@app.route('/user', methods=['POST'])
def add_users():

    request_body_user = request.get_json()
    
    new_user = User(email=request_body_user['email'], password=request_body_user['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify('user added:',request_body_user), 200

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_users(user_id):

    request_body_user = request.get_json()

    user1 = User.query.get(user_id)
    if user1 is None:
        raise APIException('watafak! no encontrado...', status_code=404)

    if 'email' in request_body_user:
        user1.email = request_body_user['email']    

    db.session.commit()
    
    return jsonify('funky user editado:',request_body_user), 200


@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_users(user_id):

    user1 = User.query.get(user_id)
    if user1 is None:
        raise APIException('watafak! no encontrado...', status_code=404)

    db.session.delete(user1)
    db.session.commit()
    
    return jsonify('funky user borrado'), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
