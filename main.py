import pickle
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models import Post 

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

# Initial Data (Global list)
posts = [
    {
        "id": 1, 
        "author": "Corey Schafer", 
        "title": "FastAPI is Awesome", 
        "content": "This framework is really easy to use and super fast for building APIs.",
        "date_posted": "April 20, 2026",
        "category": "Tech"
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
    # Create new post object
    new_post = {
        "id": len(posts) + 1,
        "author": author,
        "title": title,
        "content": content,
        "date_posted": "April 27, 2026",
        "category": "Uncategorized"
    }
    
    # Run AI Prediction immediately for the new post
    if model is not None:
        prediction = model.predict([content])
        new_post["category"] = str(prediction[0]).capitalize()
    
    # Insert at the beginning of the global list
    posts.insert(0, new_post)
    
    # Redirect to the home page to prevent form resubmission on refresh
    return RedirectResponse(url="/", status_code=303)

# --- API ROUTES (Keeping these for your docs) ---

@app.get("/api/posts")
def get_api_posts():
    return {"data": posts}

@app.post("/predict-category")
def predict_category(content: str):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")
    prediction = model.predict([content]) 
    return {"prediction": str(prediction[0])}