from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2
import psycopg2.extras
from auth_middleware import token_required
from db_helpers import get_db_connection

profile_blueprint = Blueprint('profile_blueprint', __name__)

@profile_blueprint.route('/users/<user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 1. Fetch User Details
        cursor.execute("SELECT id, username, created_at FROM users WHERE id = %s", (user_id,))
        user_info = cursor.fetchone()

        if not user_info:
            return jsonify({"error": "User not found"}), 404
        
        # fetch users friends (top 8)
        cursor.execute("""
                    SELECT u.id, u.username
                    FROM users u
                    JOIN friends f ON u.id = f.friend_id
                    WHERE f.user_id = %s
                    LIMIT 8;
                    """, (user_id,))
        friends = cursor.fetchall()

        # fetch all posts by this user only
        cursor.execute("SELECT * FROM posts WHERE user_id = %s ORDER BY id DESC", (user_id,))
        posts = cursor.fetchall()

        connection.close()

        # load it for the front end
        return jsonify({
            "user": user_info,
            "friends": friends,
            "posts": posts,
            "friend_count": len(friends)
        }), 200
    
    except Exception as error:
        return jsonify({"error": str(error)}), 500