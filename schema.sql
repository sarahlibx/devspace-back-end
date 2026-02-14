--- Users Table ---
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL
);

--- Posts Table ---
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--- Comments Table ---
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    text VARCHAR(280), 
    content TEXT NOT NULL
);

--- Friends Table ---
CREATE TABLE friends (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    friend_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, friend_id)
);

--- Profiles Table ---
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    profile_picture_url TEXT,
    bio_quote VARCHAR(140),
    fun_fact VARCHAR(100),
    fav_band VARCHAR(100),
    fav_book VARCHAR(100),
    hobbies VARCHAR(100),
    fav_language VARCHAR(100),
    email VARCHAR(255),
    github_link TEXT,
    linkedin_link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    profile_song VARCHAR(255)
);