# posts_blueprint.py
from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2
import psycopg2.extras
from auth_middleware import token_required
from db_helpers import get_db_connection, consolidate_comments_in_posts

posts_blueprint = Blueprint('posts_blueprint', __name__)

# GET posts route (the feed)
@posts_blueprint.route('/posts', methods=['GET'])
def posts_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        # JOIN users 
        query = """
            SELECT 
                posts.id,
                posts.title,
                posts.content,
                posts.created_at,
                posts.user_id AS post_author_id, 
                users.username AS author_username, 
                profiles.profile_picture_url,
                comments.id AS comment_id,
                comments.content AS comment_text,
                u_comment.username AS comment_author_username,
                comments.user_id AS comment_author_id
            FROM posts
            JOIN users ON posts.user_id = users.id
            LEFT JOIN profiles ON posts.user_id = profiles.user_id
            LEFT JOIN comments ON posts.id = comments.post_id
            LEFT JOIN users u_comment ON comments.user_id = u_comment.id
            ORDER BY posts.created_at DESC;
        """
        
        cursor.execute(query)
        posts_data = cursor.fetchall()

        # Update:
        consolidated_posts = consolidate_comments_in_posts(posts_data)

        connection.commit()
        connection.close()
        print(f"SUCCESS: Found {len(consolidated_posts)} posts")
        return jsonify(consolidated_posts), 200
    except Exception as error:
        print("!!!!!!!! BACKEND ERROR !!!!!!!!")
        print(error) 
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return jsonify({"error": str(error)}), 500

# POST create new post route
@posts_blueprint.route('/posts', methods=['POST'])
@token_required
def create_post():
    try:
        new_post = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        # 'g.user' comes from auth_middleware
        cursor.execute("""
                        INSERT INTO posts (content, user_id)
                        VALUES (%s, %s)
                        RETURNING *;
                        """,
                       (new_post['content'], g.user['id'])
                       )
        new_post_id = cursor.fetchone()["id"]

        # fetch full post to return to the front end
        cursor.execute("""SELECT p.id, 
                            p.user_id, 
                            p.content,  
                            u.username AS author_username
                        FROM posts p
                        JOIN users u  ON p.user_id = u.id
                        WHERE p.id = %s
                       """, (new_post_id,))
        
        created_post = cursor.fetchone()

        connection.commit()
        connection.close()

        return jsonify(created_post), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500

# GET post by id
@posts_blueprint.route('/posts/<post_id>', methods=['GET'])
def show_post(post_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT 
                p.id, 
                p.user_id AS post_author_id, 
                p.content, 
                u_post.username AS author_username, 
                c.id AS comment_id, 
                c.content AS comment_text, 
                u_comment.username AS comment_author_username,
                c.user_id AS comment_author_id,
                p.created_at
            FROM posts p
            INNER JOIN users u_post ON p.user_id = u_post.id
            LEFT JOIN comments c ON p.id = c.post_id
            LEFT JOIN users u_comment ON c.user_id = u_comment.id
            WHERE p.id = %s;
        """, (post_id,))
        
        posts = cursor.fetchall()
        
        consolidated_posts = consolidate_comments_in_posts(posts)
        
        connection.close()
        return jsonify(consolidated_posts[0]), 200
        
    except Exception as error:
        return jsonify({"error": str(error)}), 500

# UPDATE post by id
@posts_blueprint.route('/posts/<post_id>', methods=['PUT'])
@token_required
def update_post(post_id):
    try:
        update_post = request.json
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        #fetch post to check existence & ownership
        cursor.execute("SELECT user_id FROM posts WHERE id = %s", (post_id,))
        post_to_update = cursor.fetchone()

        if post_to_update is None:
            return jsonify({"error": "Post not found"}), 404
        connection.commit()

        if post_to_update["user_id"] != g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        
        # update content & return full updated post using JOIN in RETURNING phase
        cursor.execute("""
                       UPDATE posts 
                       SET content = %s 
                       WHERE id = %s RETURNING id, content, user_id;
                       """,(update_post["content"], post_id))
                       
        updated_post = cursor.fetchone()

        # fetch for username 
        cursor.execute("""
                       SELECT p.id, p.user_id, p.content, u.username AS author_username
                        FROM posts p
                        JOIN users u ON p.user_id = u.id
                        WHERE p.id = %s
                       """, (updated_post["id"],))
        
        updated_post = cursor.fetchone()

        connection.commit()
        connection.close()
        return jsonify(updated_post), 200
    
    except Exception as error:
        return jsonify({"error": str(error)}), 500

# DELETE post by id 
@posts_blueprint.route('/posts/<post_id>', methods=['DELETE'])
@token_required
def delete_post(post_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        # verify user owns the post before deleting
        cursor.execute("""
                       DELETE FROM posts 
                       WHERE id = %s AND user_id = %s
                       RETURNING *;
                    """, (post_id, g.user['id']))

        deleted_post = cursor.fetchone()

        if deleted_post is None:
            connection.close()
            return jsonify({"error": "Post not found or Unauthorized"}), 404
        
        connection.commit()
        connection.close()

        return jsonify(deleted_post), 200
    
    except Exception as error:
        return jsonify({"error": str(error)}), 500
