from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2
import psycopg2.extras
from auth_middleware import token_required
from db_helpers import get_db_connection

network_blueprint = Blueprint('network_blueprint', __name__)

@network_blueprint.route('/users/<int:user_id>/wall', methods=['GET'])
def get_user_profile(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Fetch User Details
        cursor.execute("SELECT id, username FROM users WHERE id = %s", (int(user_id),))
        user_info = cursor.fetchone()

        if not user_info:
            return jsonify({"error": "User not found"}), 404
        
        # fetch users friends (top 8)
        cursor.execute("""
                SELECT u.id, u.username, p.profile_picture_url
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                    WHERE u.id IN (
                    SELECT friend_id FROM friends WHERE user_id = %s
                    UNION
                    SELECT user_id FROM friends WHERE friend_id = %s
                );
                    """, (int(user_id), (int(user_id),)))
        friends = cursor.fetchall()

        # fetch all posts by this user only
        cursor.execute("SELECT * FROM posts WHERE user_id = %s ORDER BY id DESC", (int(user_id),))
        posts = cursor.fetchall()

        # TEST
        print(f"--- LIST CHECK: Number of unique friends found: {len(friends)} ---")

        connection.close()

        # load it for the front end
        return jsonify({
            "user": user_info,
            "friends": friends,
            "posts": posts,
            "friend_count": len(friends)
        }), 200
    
    except Exception as error:
        print(f"CRASH IN NETWORK_BP: {error}")
        return jsonify({"error": str(error)}), 500
    
# search for user by name
@network_blueprint.route('/users/search/<query>', methods=['GET'])
@token_required
def search_users(query):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        search_query = f"%{query}%"
        cursor.execute("""
            SELECT id, username FROM users 
            WHERE username ILIKE %s AND id != %s
            LIMIT 20
        """, (search_query, g.user['id']))

        results = cursor.fetchall()
        connection.close()
        return jsonify(results), 200
    except Exception as error:
        return jsonify({'error': str(error)}), 500