
![money-mentor](im.png)

# Backend

A RESTful API for managing users, transactions, categories, summaries, and mentor feedback for the Money Mentor application.

Built with Node.js, Express, and MongoDB.
add the link to the front the name of the project

---

Money Mentor’s backend handles authentication, data persistence, authorization, and business logic for tracking personal finances and points-based progress.

## Tech Stack

- Node.js
- Express
- MongoDB
- Mongoose
- JSON Web Tokens (JWT)
- bcrypt
- dotenv

---

## Getting started

1. Install dependencies
npm i
npm install @google/genai

2. Create a `.env` file with:
- MONGODB_URI=your_mongo_connection_string
- JWT_SECRET=your_secret
- PORT=your_port
- GEMINI_API_KEY=your_real_Gemini_AI_key

3. Start the server
npm run dev

### Frontend Repository
The frontend repository for this project can be found here:  
[Frontend](https://github.com/angelikakasia/money-mentor-front-end)

---

## Features

- User authentication (signup, login)
- JWT-based authorization
- Owner-only access to user data
- Full CRUD for transactions
- Predefined categories linked to users
- Monthly summary calculations
- Mentor logic and points system
- Level progression based on points

----

## Data Models

### User
- username
- password (hashed)
- points

### Transaction
- amount
- type (Income / Expense)
- category
- date
- user

### Category
- name
- type
- user

---

## Middleware

- JWT verification middleware protects all non-auth routes
- Authorization ensures users can only access their own data

---

## Development Team

This project was built by:

- **Sarah Smith** - |[GitHub](https://github.com/sarahlibx) | [LinkedIn](https://www.linkedin.com/in/sarahsmithdeveloper/) |


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
