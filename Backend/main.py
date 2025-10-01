import os
import json
import shutil
import time
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Import everything from your corrected database.py
from database import SessionLocal, User, Meeting, Task, create_db_and_tables

# --- INITIALIZATION ---

# Create the database tables on startup if they don't exist
create_db_and_tables()

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: Gemini API Key not found. Please check your .env file.")

# Create the FastAPI app instance
app = FastAPI(title="Meeting Agent API")

# --- MIDDLEWARE ---
# Add CORS middleware to allow your frontend (running on a different port) to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. In production, change to your frontend's URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- AUTHENTICATION (SIMPLE, INSECURE PROTOTYPE) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(db: Session, username: str, password: str):
    """Checks credentials using plain-text password comparison."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.password == password:
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Gets the user object from the token (which is just the username)."""
    user = db.query(User).filter(User.username == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# --- API ENDPOINTS ---

@app.post("/token", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint that returns a simple token (the username)."""
    user = authenticate_user(db, form_data.username.lower(), form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/users/me", tags=["Users"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Returns the current logged-in user's info."""
    return {"username": current_user.username, "id": current_user.id}

@app.get("/users/me/tasks", tags=["Tasks"])
async def read_user_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns all tasks assigned to the current logged-in user."""
    tasks = db.query(Task).filter(Task.assignee_id == current_user.id).all()
    return tasks

@app.post("/process-meeting/", tags=["Meeting Processing"])
async def process_meeting(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Protected endpoint to process an audio file for the logged-in user.
    """
    temp_file_path = f"temp_{file.filename}"
    audio_file_resource = None # To ensure cleanup happens
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Upload file to Gemini and wait for it to be active
        print("Uploading file to Gemini...")
        audio_file_resource = genai.upload_file(path=temp_file_path)
        while audio_file_resource.state.name == "PROCESSING":
            time.sleep(2)
            audio_file_resource = genai.get_file(audio_file_resource.name)
        if audio_file_resource.state.name != "ACTIVE":
            raise Exception("File processing failed on Google's servers.")
        
        # 2. Process with Gemini model
        print("Processing with Gemini...")
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest') # Or your available model
        prompt = """Analyze the audio. Respond with a JSON object with keys "minutes" (a summary) and "tasks" (a list of objects with "task_description", "assignee", and "due_date")."""
        
        response = model.generate_content([prompt, audio_file_resource], generation_config=genai.types.GenerationConfig(response_mime_type="application/json"))
        ai_results = json.loads(response.text)
        print("Processing complete.")

        # 3. Save results to the database
        new_meeting = Meeting(filename=file.filename, summary=ai_results.get("minutes"), date=datetime.utcnow().date())
        db.add(new_meeting)
        db.commit()
        db.refresh(new_meeting)

        tasks_to_save = ai_results.get("tasks", [])
        for task_item in tasks_to_save:
            assignee_name_raw = task_item.get("assignee", "")
            assignee_name = (assignee_name_raw[0] if isinstance(assignee_name_raw, list) else assignee_name_raw).lower()
            
            assignee_user = db.query(User).filter(User.username == assignee_name).first()
            if assignee_user:
                new_task = Task(description=task_item.get("task_description"), due_date_str=task_item.get("due_date"), meeting_id=new_meeting.id, assignee_id=assignee_user.id)
                db.add(new_task)
        db.commit()

        return {"meeting_info": {"id": new_meeting.id, "filename": file.filename}, "results": ai_results}

    except Exception as e:
        # Clean up Gemini file on error
        if audio_file_resource:
            genai.delete_file(audio_file_resource.name)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        # Clean up local temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        # Clean up Gemini file on success
        if audio_file_resource:
            genai.delete_file(audio_file_resource.name)
            print(f"Cleaned up remote file: {audio_file_resource.name}")