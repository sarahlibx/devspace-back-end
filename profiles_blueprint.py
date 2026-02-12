from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2.extras
from auth_middleware import token_required
from main import upload_image

profiles_blueprint = Blueprint('profiles_blueprint', __name__)

# GET a profile (either your own or someone else's)
@profiles_blueprint.route('/profiles/<user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("SELECT * FROM profiles WHERE user_id = %s", (user_id,))
        profile = cursor.fetchone()
        
        connection.close()
        if not profile:
            return jsonify({"message": "No profile setup yet"}), 200 # Return empty instead of error
        return jsonify(profile), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

# POST/PUT to create or update your own profile
@profiles_blueprint.route('/profiles', methods=['POST'])
@token_required
def upsert_my_profile():
    try:
        image = request.files.get('photo')
        text_data = request.form

        profile_picture_url = text_data.get('profile_picture_url')
        if image:
            print("--- Uploading to Cloudinary ---")
            profile_picture_url = upload_image(image)
            print(f"--- New URL: {profile_picture_url} ---")

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            INSERT INTO profiles (
                user_id, profile_picture_url, bio_quote, fun_fact, fav_band, 
                fav_book, hobbies, fav_language, 
                email, github_link, linkedin_link
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET
                profile_picture_url = EXCLUDED.profile_picture_url, 
                bio_quote = EXCLUDED.bio_quote,
                fun_fact = EXCLUDED.fun_fact,
                fav_band = EXCLUDED.fav_band,
                fav_book = EXCLUDED.fav_book,
                hobbies = EXCLUDED.hobbies,
                fav_language = EXCLUDED.fav_language,
                email = EXCLUDED.email,
                github_link = EXCLUDED.github_link,
                linkedin_link = EXCLUDED.linkedin_link
            RETURNING *;
        """, (
            g.user['id'],
            profile_picture_url, 
            text_data.get('bio_quote'), 
            text_data.get('fun_fact'), 
            text_data.get('fav_band'), 
            text_data.get('fav_book'), 
            text_data.get('hobbies'), 
            text_data.get('fav_language'), 
            text_data.get('email'), 
            text_data.get('github_link'), 
            text_data.get('linkedin_link')
        ))

        profile = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify(profile), 200
    except Exception as error:
        print("!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ACTUAL SERVER ERROR:", str(error))
        print("!!!!!!!!!!!!!!!!!!!!!!!!")
        return jsonify({"error": str(error)}), 500