import pickle
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Setup Templates
templates = Jinja2Templates(directory="templates")

# Load ML Model
try:
    with open("LogisticRegression.pickle", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    model = None
    print(f"Warning: Model could not be loaded. {e}")

# Initial Data (Using a list that we can modify)
posts = [
    {
        "id": 1, 
        "author": "Corey Schafer", 
        "title": "FastAPI is Awesome", 
        "content": "This framework is really easy to use and super fast for building APIs.",
        "date_posted": "April 20, 2026",
        "category": "Tech"
    },
    {
        "id": 2, 
        "author": "AI Assistant",
        "title": "Welcome to the App", 
        "content": "This is a sample post to get you started.", 
        "date_posted": "April 27, 2026",
        "category": "General"
    }
]

# --- WEB ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def render_blog(request: Request):
    # Ensure all posts have categories via AI if missing
    for post in posts:
        if "category" not in post or post["category"] == "Uncategorized":
            if model is not None:
                prediction = model.predict([post["content"]])
                post["category"] = str(prediction[0]).capitalize()
    
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"posts": posts}
    )

@app.post("/add-post")
async def add_post(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    content: str = Form(...)
):
    # Robust ID Generation: Find the current max ID and add 1
    # This prevents duplicate IDs after deletions
    new_id = max([p["id"] for p in posts], default=0) + 1
    
    new_post = {
        "id": new_id,
        "author": author,
        "title": title,
        "content": content,
        "date_posted": "April 27, 2026",
        "category": "Uncategorized"
    }
    
    if model is not None:
        prediction = model.predict([content])
        new_post["category"] = str(prediction[0]).capitalize()
    
    posts.insert(0, new_post)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{post_id}")
async def delete_post(post_id: int):
    global posts
    # Keep every post except the one that matches the post_id
    posts = [p for p in posts if p["id"] != post_id]
    return RedirectResponse(url="/", status_code=303)

# --- API ROUTES ---

@app.get("/api/posts")
def get_api_posts():
    return {"data": posts}

@app.post("/predict-category")
def predict_category(content: str):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")
    prediction = model.predict([content]) 
    return {"prediction": str(prediction[0])}