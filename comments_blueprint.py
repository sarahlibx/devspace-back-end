from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2.extras
from auth_middleware import token_required

comments_blueprint = Blueprint('comments_blueprint', __name__)
    
# GET all comments on a specific post
@comments_blueprint.route('/posts/<post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # JOIN with users to get the commenter's username
        cursor.execute("""
            SELECT c.id, c.content, c.user_id, u.username
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.id ASC;
        """, (post_id,))
        
        comments = cursor.fetchall()
        connection.close()
        return jsonify(comments), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

# POST create new comment route
@comments_blueprint.route('/posts/<post_id>/comments', methods=['POST'])
@token_required
def create_comment(post_id):
    try:
        new_comment_data = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
                        INSERT INTO comments (post_id, user_id, content)
                        VALUES (%s, %s, %s)
                        RETURNING *;
                        """,
                       (post_id, g.user['id'], new_comment_data['content'])
                       )
        
        new_comment_id = cursor.fetchone()['id']

        cursor.execute("""SELECT c.*, u.username AS comment_author_username
                        FROM comments c
                        JOIN users u ON c.user_id = u.id
                        WHERE c.id = %s
                       """, (new_comment_id,))
        
        created_comment = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify(created_comment), 201
    
    except Exception as error:
        return jsonify({"error": str(error)}), 500

# PUT/UPDATE comment by id
@comments_blueprint.route('/posts/<post_id>/comments/<comment_id>', methods=['PUT'])
@token_required
def update_comment(comment_id):
    try:
        updated_comment_data = request.json
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        # ownership check
        cursor.execute("SELECT user_id FROM comments WHERE id = %s", (comment_id,))
        comment_to_update = cursor.fetchone()

        if comment_to_update is None:
            return jsonify({"error": "Comment not found"}), 404
        
        if comment_to_update["user_id"] != g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        
        # update the comment
        cursor.execute("UPDATE comments SET content = %s WHERE id = %s RETURNING *",
                       (updated_comment_data["content"], comment_id))
        
        updated_comment = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"comment": updated_comment}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
# GET specific comment by id 
@comments_blueprint.route('/posts/<post_id>/comments/<comment_id>', methods=['GET'])
def show_comment(comment_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT c.*, u.username 
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = %s
        """, (comment_id,))
        
        comment = cursor.fetchone()
        connection.close()
        
        if not comment:
            return jsonify({"error": "Comment not found"}), 404
            
        return jsonify(comment), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

# DELETE comment by id (and by author of comment)
@comments_blueprint.route('/posts/<post_id>/comments/<comment_id>', methods=['DELETE'])
@token_required
def delete_comment(comment_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        # ownership check 
        cursor.execute("""
                    DELETE FROM comments 
                    WHERE id = %s AND user_id = %s 
                    RETURNING id;
                """, (comment_id, g.user['id']))

        comment_to_delete = cursor.fetchone()
        
        if comment_to_delete is None:
            return jsonify({"error": "Comment not found"}), 404
        
        if comment_to_delete["user_id"] != g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        
        connection.commit()
        connection.close()
        return jsonify({"message": "Comment deleted successfully"}), 200
    
    except Exception as error:
        return jsonify({"error": str(error)}), 500
