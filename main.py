import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select

load_dotenv()

if(os.getenv("IS_LOCAL") == False):
    DATABASE_URL = os.getenv("POSTGRES_URL_NON_POOLING", "sqlite:///database.db")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    DATABASE_URL = os.getenv("sqlite:///database.db", "sqlite:///database.db")


if not DATABASE_URL:
    raise ValueError("DATABASE_URL or POSTGRES_URL_NON_POOLING not set in environment.")



engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

class PostBase(SQLModel):
    title: str
    content: str


class Post(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author_ip: str = Field(max_length=45)  # Store the IP of the creator


class PostCreate(PostBase):
    title: str
    content: str


class PostUpdate(PostBase):
    title: str
    content: str

SQLModel.metadata.create_all(engine)

app = FastAPI(title="InterLink API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_client_ip(request: Request):
    # Check for x-forwarded-for header (common for proxies/load balancers)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Take the first IP in case there are multiple
        return forwarded.split(",")[0].strip()
    
    # Check for x-real-ip header (used by some proxies)
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to request.client.host
    return request.client.host


@app.get("/")
def root(request: Request):
    client_ip = get_client_ip(request)
    return {"status": "active", "your_ip": client_ip}


@app.get("/posts")
def get_posts(request: Request, password:str | None = None):
    client_ip = get_client_ip(request)
    with Session(engine) as session:
        if password:
            if password == os.getenv("ADMIN_PASSWORD"):
                posts = session.exec(select(Post)).all()
                return posts
            else:
                raise HTTPException(status_code=403, detail="Wrong Password")
        else:
            # Only return posts created by the current IP
            posts = session.exec(select(Post).where(Post.author_ip == client_ip)).all()
            return posts

@app.post("/posts")
def create_post(request: Request, post: PostCreate):
    client_ip = get_client_ip(request)
    # add ip to the post
    post_with_ip = Post(title=post.title, content=post.content, author_ip=client_ip)
    with Session(engine) as session:
        session.add(post_with_ip)
        session.commit()
        session.refresh(post_with_ip)
        return post_with_ip


@app.put("/posts/{post_id}")
def update_post(request: Request, post_id: int, post_update: PostUpdate):
    client_ip = get_client_ip(request)
    with Session(engine) as session:
        # find the post
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # verify access
        if post.author_ip != client_ip:
            raise HTTPException(status_code=403, detail="Not authorized to update this post")
        
        # Update the post
        post.title = post_update.title
        post.content = post_update.content
        session.commit()
        session.refresh(post)
        return post


@app.delete("/posts/{post_id}")
def delete_post(request: Request, post_id: int):
    client_ip = get_client_ip(request)
    with Session(engine) as session:
        # find the post
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # verify access
        if post.author_ip != client_ip:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
        # deleting the post
        session.delete(post)
        session.commit()
        return {"message": "Post deleted successfully"}