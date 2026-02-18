import os
import psycopg2

def get_db_connection():
    if 'ON_HEROKU' in os.environ:
        connection = psycopg2.connect(
            os.getenv('DATABASE_URL'), 
            sslmode='require'
        )
    else:
        connection = psycopg2.connect(
            host='localhost',
            database=os.getenv('POSTGRES_DATABASE'),
            user=os.getenv('POSTGRES_USERNAME'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
    return connection


def consolidate_comments_in_posts(posts_with_comments):
    consolidated_posts = []

    for row in posts_with_comments:
        # Check if this post has already been added to consolidated_posts
        existing_post = next((p for p in consolidated_posts if p["id"] == row["id"]), None)

        if existing_post:
            # If the post exists and there's a comment in this row, add it
            if row["comment_id"]:
                existing_post["comments"].append({
                    "id": row["comment_id"],
                    "title": row.get("title"),
                    "content": row["comment_text"],
                    "author_username": row["comment_author_username"],
                    "user_id": row["comment_author_id"]
                })
        else:
            # Create the base post object
            new_post = {
                "id": row["id"],
                "user_id": row.get("post_author_id") or row.get("user_id"),
                "title": row.get("title"),
                "content": row["content"],
                "author_username": row["author_username"],
                "profile_picture_url": row.get("profile_picture_url"),
                "created_at": row["created_at"],
                "comments": []
            }
            
            # If the first row retrieved has a comment, add it
            if row["comment_id"]:
                new_post["comments"].append({
                    "id": row["comment_id"],
                    "content": row["comment_text"],
                    "author_username": row["comment_author_username"],
                    "user_id": row["comment_author_id"]
                })
            
            consolidated_posts.append(new_post)

    return consolidated_posts
