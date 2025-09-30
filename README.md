# Meeting Agent Web Application

This project is a web-based tool that takes a meeting audio file, processes it using the Google Gemini API to generate a summary and a list of action items, and saves the results to a database.

## Project Structure

The project is organized into two main folders: `Backend` for the server-side logic and `Frontend` for the user interface.


## Prerequisites

Before you begin, ensure you have the following installed on your system:
* **Python** (version 3.8 or higher)
* **Node.js** and **npm** (version 18 or higher)
* **Git** (for version control)

## Setup and Installation

Follow these steps to get the project running locally.

### Backend Setup

1.  **Navigate to the Backend Directory**:
    Open a terminal and change to the backend folder.
    ```bash
    cd Backend
    ```

2.  **Create and Activate a Virtual Environment**:
    ```bash
    # Create the environment
    python -m venv venv
    
    # Activate the environment
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Install Python Dependencies**:
    Install all required libraries from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create Environment File**:
    Create a file named `.env` in the `Backend` folder and add your Gemini API key.
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```

### Frontend Setup

1.  **Navigate to the Frontend Directory**:
    Open a **new, separate terminal** and change to the frontend folder.
    ```bash
    cd Frontend/frontend
    ```

2.  **Install Node.js Dependencies**:
    ```bash
    npm install
    ```

## Running the Application

You need to run both the backend and frontend servers simultaneously in their separate terminals.

### 1. Start the Backend Server

* In your **backend terminal** (with the virtual environment active):
    ```bash
    uvicorn main:app --reload
    ```
* The backend server will be running at `http://127.0.0.1:8000`.

### 2. Start the Frontend Server

* In your **frontend terminal**:
    ```bash
    npm run dev
    ```
* The frontend website will be running at `http://localhost:5173` (or a similar address shown in the terminal).

Open your web browser and navigate to the frontend URL to use the application.

---

## How to Edit the Project

This section details exactly which files to modify for common changes.

### Backend Modifications

Your main work in the backend will be in the `Backend/` folder.

* **To change API logic, add new endpoints, or modify AI processing**:
    * Edit **`main.py`**. This is the core of your application. It contains all the API routes (like `/process-audio/`) and orchestrates the calls to the Gemini API and the database.

* **To change the database structure (e.g., add new columns to tasks)**:
    * Edit **`database.py`**. This file defines the SQLAlchemy models, which correspond to your database tables (`Meeting`, `Task`).

* **To add a new Python library**:
    * First, install it with pip: `pip install new-library-name`
    * Then, update your requirements file: `pip freeze > requirements.txt`

### Frontend Modifications

Your main work in the frontend will be in the `Frontend/frontend/src/` folder.

* **To change the main layout and state management**:
    * Edit **`src/App.jsx`**. This file is the main component that holds the application's state (like the uploaded file, loading status, and results) and assembles the other components.

* **To change the UI elements**:
    * Edit files in the **`src/components/`** directory.
        * **`UploadForm.jsx`**: Controls the file input and the "Analyze Meeting" button.
        * **`ResultsDisplay.jsx`**: Controls how the summary and task list are displayed.

* **To change the website's appearance (colors, fonts, layout)**:
    * Edit **`src/App.css`**. This file contains all the styling for the application.

* **IMPORTANT: Connecting to the Backend**:
    * The link between your frontend and backend is defined in **`src/App.jsx`**.
    * Look for this line: `const API_URL = 'http://127.0.0.1:8000/process-audio/';`
    * When you deploy your backend to a live server (like Render), you will need to **change this URL** to your live backend address.
