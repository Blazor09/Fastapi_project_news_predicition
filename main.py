import pickle
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from models import Post  # Ensure Post is defined in models.py

app = FastAPI()

# Load your model once at startup
try:
    with open("LogisticRegression.pickle", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    model = None
    print("Warning: LogisticRegression.pickle not found.")

# Updated data with date_posted to prevent KeyErrors
posts = [
    {
        "id": 1, 
        "author": "Corey Schafer", 
        "title": "FastAPI is Awesome", 
        "content": "This framework is really easy to use.",
        "date_posted": "April 20, 2025"
    },
    {
        "id": 2, 
        "author": "Jane Doe", 
        "title": "Python for Web", 
        "content": "Python is great for development.",
        "date_posted": "April 21, 2025"
    }
]

# --- API ROUTES (JSON) ---

@app.get("/api/posts")
def get_posts():
    return {"data": posts}

@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/api/posts", status_code=201)
def create_post(post: Post):
    post_dict = post.model_dump()
    posts.append(post_dict)
    return post_dict

# --- ML ROUTE ---

@app.post("/predict-category")
def predict_category(content: str):
    # 1. Explicitly check if model exists
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail="Model is not available on this server."
        )
    
    # 2. Now Pylance knows 'model' cannot be None beyond this point
    prediction = model.predict([content]) 
    return {"prediction": str(prediction[0])}
# --- WEB ROUTES (HTML) ---

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return "<h1>Hello World</h1><p>Visit <a href='/blog'>/blog</a> to see posts.</p>"

@app.get("/blog", response_class=HTMLResponse, include_in_schema=False)
def home():
    content = ""
    for post in posts:
        content += f"""
        <div style="margin-bottom: 20px; border-bottom: 1px solid #ccc;">
            <h2>{post['title']}</h2>
            <p><strong>By:</strong> {post['author']}</p>
            <p>{post['content']}</p>
            <small>{post.get('date_posted', 'No date')}</small>
        </div>
        """
    return f"<html><body style='font-family: sans-serif; max-width: 800px; margin: auto;'>{content}</body></html>"