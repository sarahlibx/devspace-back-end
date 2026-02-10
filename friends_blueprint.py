from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2.extras
from auth_middleware import token_required

friends_blueprint = Blueprint('friends_blueprint', __name__)

# POST add a friend
@friends_blueprint.route('/friends/<friend_id>', methods=["POST"])
@token_required
def add_friend(friend_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # prevent adding yourself
        if int(friend_id) == g.user['id']:
            return jsonify({"error": "You cannot add yourself as a friend"}), 400
        
        # check if friendship already exists
        cursor.execute("SELECT * FROM friends WHERE user_id = %s AND friend_id = %s", (g.user['id'], friend_id))

        if cursor.fetchone():
            return jsonify({"error": "You are already friends!"}), 400
        
        # create the friendship
        cursor.execute("""
                    INSERT INTO friends (user_id, friend_id)
                    VALUES (%s, %s) RETURNING *;
                    """, (g.user['id'], friend_id))
        
        connection.commit()
        connection.close()
        return jsonify({"message": "Friend added successfully!"}), 201
    
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
# GET list of all friends for logged in user
@friends_blueprint.route('/friends', methods=['GET'])
@token_required
def get_friends():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # JOIN with the users table to get the names of the friends
        cursor.execute("""
            SELECT u.id, u.username
            FROM users u
            JOIN friends f ON u.id = f.friend_id
            WHERE f.user_id = %s;
        """, (g.user['id'],))
        
        friends_list = cursor.fetchall()
        connection.close()
        return jsonify(friends_list), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
# DELETE unfriend someone
@friends_blueprint.route('/friends/<friend_id>', methods=['DELETE'])
@token_required
def unfriend(friend_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Attempt to delete the specific friendship row
        # check both user_id (you) and friend_id (them)
        cursor.execute("""
            DELETE FROM friends 
            WHERE user_id = %s AND friend_id = %s
            RETURNING *;
        """, (g.user['id'], friend_id))
        
        deleted_relationship = cursor.fetchone()

        # If nothing was returned, the friendship didn't exist
        if not deleted_relationship:
            connection.close()
            return jsonify({"error": "Friendship not found"}), 404
            
        connection.commit()
        connection.close()
        return jsonify({"message": "Successfully unfriended"}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500