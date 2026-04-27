import pickle
from datetime import datetime
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
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"posts": posts}
    )

@app.post("/add-post")
async def add_post(
    title: str = Form(...),
    author: str = Form(...),
    content: str = Form(...)
):
    # 1. Generate unique ID based on current max
    new_id = max([p["id"] for p in posts], default=0) + 1
    
    # 2. Prepare content for AI (lowercase helps matching)
    clean_content = content.lower().strip()
    category = "Uncategorized"
    
    # 3. Predict Category
    if model is not None:
        prediction = model.predict([clean_content])
        category = str(prediction[0]).capitalize()
        # Log to terminal for debugging
        print(f"DEBUG AI: Input: {clean_content[:30]}... -> Predicted: {category}")

    # 4. Create new post dictionary
    new_post = {
        "id": new_id,
        "author": author,
        "title": title,
        "content": content,
        "date_posted": datetime.now().strftime("%B %d, %Y"),
        "category": category
    }
    
    posts.insert(0, new_post)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{post_id}")
async def delete_post(post_id: int):
    global posts
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
    prediction = model.predict([content.lower().strip()]) 
    return {"prediction": str(prediction[0])}