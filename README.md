
<div id="header" align="center">

<img width="713" height="62" alt="devspace-banner" src="https://github.com/user-attachments/assets/deafc925-451e-44a4-b3bd-f688c1e7f7bf" />

</div>

# DevSpace Backend

A RESTful networking app for managing users, profiles, posts, comments, and connection!

Built with Python, Flask & PostgreSQL.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

---

DevSpace's backend handles authentication, data persistence, authorization, and network connection logic for adding friends, posts, comments and customizing a personalized profile.

## Tech Stack

- Python3
- Flask
- PostgreSQL
- JSON Web Tokens (JWT)
- Cloudinary API
- bcrypt
- dotenv

---

## Getting started

Fork and clone this repository to your local machine.

After moving into the cloned directory, activate a new virtual environment:

```bash
pipenv shell
```

Install the dependencies:

```bash
pyenv sync
```

Run the Flask app:

```bash
python app.py
```

To deactivate the virtual environment when you're done, run:

```bash
exit
```

Don't forget to create a `.env` file with:
- JWT_SECRET=<your_secret>
- POSTGRES_USERNAME=<your_username>
- POSTGRES_PASSWORD=<your-password>
- POSTGRES_DATABASE=<database_name>
- API_KEY=<your_cloudinary_key>
- API_SECRET=<your_cloudinary_secret>

### Frontend Repository
The frontend repository for this project can be found here:  
[Frontend](https://github.com/sarahlibx/devspace-front-end)

---

## Features

- User authentication (signup, login)
- JWT-based authorization
- Owner-only access to user data
- Full CRUD for network posts
- Fully customizable user profile
- iTunes API integration for profile song
- The app uses dynamic CORS origins to allow for both local development and production environments.
-- Production: Set FRONTEND_URL in Heroku to your Netlify domain.
-- Development: Defaults to localhost:5173

----

## Data Models

### Users
- id
- username
- password (hashed)

### Posts
- id
- user_id
- title
- content
- created_at

### Comments
- id
- user_id
- post_id
- text
- content

### Friends
- user_id
- friend_id

### Profiles
- id
- user_id
- profile_picture_url
- bio_quote
- fun_fact
- fav_band
- fav_book
- hobbies
- fav_language
- email
- github_link
- linkedin_link
- created_at
- profile_song

---

## Middleware

- JWT verification middleware protects all non-auth routes
- Authorization ensures users can only access their own data

---

## API Endpoints
| Method | Endpoint | Description | Auth Required |
|:---|:---:|:---:|---:|
| POST | /auth/sign-up | create new user | No |
| POST | /auth/login | authenticate user & return JWT | No |
| GET | /users/<id>/wall | fetch user profile & data | Yes |
| POST | /posts | create new post | Yes |
| GET | /users/search/<query> | search for other users by username | Yes |

---

## Future Enhancements
[ ] Implement "Like" functionality on posts.

[ ] Implement edit & delete functionality on comments.

[ ] Add real-time notifications for friend requests.

[ ] Add real-time "online now" status.

[ ] Update logic for number of posts displayed to the feed & on the user profile (ex: most recent 10 then load next 10 on scroll).

[ ] Modify edit song feature to be handled directly from profile view vs in edit profile form.

[ ] Add delete friend handler logic.

[ ] Add /friends route to view all friends on a page.

[ ] Update top 8 view to be selected & set by the user, rather than current view of first 8 friends in the list.

[ ] Expand the iTunes API integration to allow for a playable music widget.

[ ] Create seed.py file for immediate "stock" database entries, making testing quicker.

---

## Development Team

This project was built by:

- **Sarah Smith** - |[GitHub](https://github.com/sarahlibx) | [LinkedIn](https://www.linkedin.com/in/sarahsmithdeveloper/) |
