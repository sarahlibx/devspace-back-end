from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
import psycopg2.extras

from auth_middleware import token_required
from auth_blueprint import authentication_blueprint
from posts_blueprint import posts_blueprint
from comments_blueprint import comments_blueprint
from friends_blueprint import friends_blueprint
from network_blueprint import network_blueprint
from profiles_blueprint import profiles_blueprint

app = Flask(__name__)
CORS(app)
app.register_blueprint(authentication_blueprint)
app.register_blueprint(posts_blueprint)
app.register_blueprint(comments_blueprint)
app.register_blueprint(friends_blueprint)
app.register_blueprint(network_blueprint)
app.register_blueprint(profiles_blueprint)

def get_db_connection():
    connection = psycopg2.connect(
        host='localhost',
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USERNAME'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    return connection


@app.route('/users')
@token_required
def users_index():
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT id, username FROM users;")
    users = cursor.fetchall()
    connection.close()
    return jsonify(users), 200


@app.route('/users/<user_id>')
@token_required
def users_show(user_id):
    if int(user_id) != g.user["id"]:
        return jsonify({"err": "Unauthorized"}), 403
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT id, username FROM users WHERE id = %s;", (user_id,))
    user = cursor.fetchone()
    connection.close()
    if user is None:
        return jsonify({"err": "User not found"}), 404
    return jsonify(user), 200

if __name__ == '__main__':
    app.run()
