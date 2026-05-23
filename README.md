# InterLink API

A simple FastAPI backend built for **Interlink Club** at the University of Biskra.

This project is designed to help students understand how APIs, servers, and databases work through a small and practical example. It shows how to build a CRUD API with FastAPI, store data with SQLModel, and apply simple access control using the client's IP address.

## Features

- Create, read, update, and delete posts
- Store posts in SQLite locally or PostgreSQL in production
- Restrict update and delete actions to the post owner
- Allow admin access to view all posts with a password
- Automatically detect client IP from proxy headers or direct requests
- Enable CORS for frontend integration

## Tech Stack

- Python
- FastAPI
- SQLModel
- SQLite
- PostgreSQL
- python-dotenv

## How It Works

Each post contains:

- `id`
- `title`
- `content`
- `author_ip`

When a user creates a post, the API stores the request IP as `author_ip`. Later, the same IP is used to decide whether that user can view, edit, or delete the post.

This keeps the project simple for learning purposes, while still introducing the idea of ownership and authorization.

## Environment Variables

Create a `.env` file in the project root.

```env
IS_LOCAL=True
POSTGRES_URL_NON_POOLING=postgresql://user:password@host:5432/dbname
ADMIN_PASSWORD=your_admin_password
```

### Variables

- `IS_LOCAL`: Set to `True` for local development and `False` for production
- `POSTGRES_URL_NON_POOLING`: PostgreSQL connection string used when `IS_LOCAL=False`
- `ADMIN_PASSWORD`: Password that allows access to all posts

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/interlink-api.git
cd interlink-api
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate it:

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install fastapi uvicorn sqlmodel python-dotenv
```

5. Run the server:

```bash
uvicorn main:app --reload
```

6. Open the docs in your browser:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### `GET /`

Returns the API status and the detected client IP.

Example response:

```json
{
  "status": "active",
  "your_ip": "127.0.0.1"
}
```

### `GET /posts`

Returns posts created by the current IP.

Optional query parameter:

- `password`: If it matches `ADMIN_PASSWORD`, the API returns all posts

Example:

```text
GET /posts?password=your_admin_password
```

### `POST /posts`

Creates a new post.

Example request body:

```json
{
  "title": "My first post",
  "content": "Hello from FastAPI"
}
```

### `PUT /posts/{post_id}`

Updates a post if the current IP matches the original creator IP.

Example request body:

```json
{
  "title": "Updated title",
  "content": "Updated content"
}
```

### `DELETE /posts/{post_id}`

Deletes a post if the current IP matches the original creator IP.

## Database Behavior

- When running locally, the app uses SQLite by default
- When `IS_LOCAL=False`, the app uses `POSTGRES_URL_NON_POOLING`
- Tables are created automatically on startup with `SQLModel.metadata.create_all(engine)`

## Learning Purpose

This project is meant for beginners who want to learn:

- How to build an API with FastAPI
- How CRUD operations work
- How to connect an application to a database
- How request data and headers are handled
- How basic authorization rules can be applied
- How local and production environments differ

## Important Notes

- This project is for education and experimentation
- IP-based authorization is not secure for real production systems
- Real applications should use proper authentication such as sessions, tokens, or JWT
- CORS is currently open to all origins, which is convenient for learning but not ideal for production

## Possible Improvements

- Add user authentication
- Hash and protect admin credentials better
- Add pagination for posts
- Validate input more strictly
- Add timestamps such as `created_at` and `updated_at`
- Split the code into routers, models, and database modules
- Add Docker support and deployment instructions

## License

This project is open for educational use.
