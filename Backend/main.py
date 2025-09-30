import os
import json
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Meeting, Task, create_db_and_tables

# --- INITIALIZATION ---

# Create the database tables if they don't exist
create_db_and_tables()

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️ Gemini API Key not found. Please check your .env file.")

# Create the FastAPI app instance
app = FastAPI(title="Meeting Analyzer API")

# Add CORS middleware to allow your future frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity
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

# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Meeting Analyzer API"}

@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    This endpoint takes an audio file, processes it, and saves the results.
    """
    # 1. Save the uploaded file to a temporary location
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Upload the file to the Gemini API (for models that support audio)
        print("Uploading file to Gemini...")
        audio_file = genai.upload_file(path=temp_file_path)
        print(f"File upload complete: {audio_file.name}")

        # 3. Call the Gemini model to process the audio
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = """
        Analyze the following meeting audio. Your tasks are to:
        1. Generate a concise "Minutes of Meeting" summary.
        2. Extract all action items into a structured list.

        Respond with a single, valid JSON object with two keys: "minutes" and "tasks".
        Each task object must have keys: "task_description", "assignee", and "due_date".
        """
        
        print("Processing with Gemini...")
        response = model.generate_content(
            [prompt, audio_file],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        ai_results = json.loads(response.text)
        print("Processing complete.")

        # 4. Save the results to the database
        # Create a new meeting record
        new_meeting = Meeting(
            filename=file.filename,
            summary=ai_results.get("minutes")
        )
        db.add(new_meeting)
        db.commit()
        db.refresh(new_meeting)

        # Save each extracted task
        tasks_to_save = ai_results.get("tasks", [])
        for task_item in tasks_to_save:
            new_task = Task(
                description=task_item.get("task_description"),
                assignee=str(task_item.get("assignee")),
                due_date_str=task_item.get("due_date"),
                meeting_id=new_meeting.id # Link the task to the meeting
            )
            db.add(new_task)
        db.commit()

        return {"meeting_info": {"id": new_meeting.id, "filename": new_meeting.filename}, "results": ai_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)