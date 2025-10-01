import { useState, useEffect } from 'react';
import axios from 'axios';

// A small component for the meeting uploader
function MeetingUploader({ token }) {
    const [file, setFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            setMessage('Please select a file first.');
            return;
        }
        setIsLoading(true);
        setMessage('Processing meeting... this may take a moment.');

        const formData = new FormData();
        formData.append('file', file);

        try {
            await axios.post('http://127.0.0.1:8000/process-meeting/', formData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setMessage('Meeting processed successfully! Your new tasks will appear on refresh.');
        } catch (error) {
            setMessage('Error processing meeting.');
            console.error(error);
        } finally {
            setIsLoading(false);
            setFile(null);
        }
    };

    return (
        <div className="uploader-section">
            <h3>Process a New Meeting</h3>
            <input type="file" onChange={handleFileChange} accept="audio/*" />
            <button onClick={handleUpload} disabled={isLoading}>
                {isLoading ? 'Analyzing...' : 'Upload & Analyze'}
            </button>
            {message && <p>{message}</p>}
        </div>
    );
}


function Dashboard({ token, onLogout }) {
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const userRes = await axios.get('http://127.0.0.1:8000/users/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(userRes.data);

        const tasksRes = await axios.get('http://127.0.0.1:8000/users/me/tasks', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setTasks(tasksRes.data);
      } catch (error) {
        console.error("Failed to fetch user data. Token might be invalid.", error);
        onLogout(); // Log out if token is invalid
      }
    };

    fetchUserData();
  }, [token, onLogout]);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Welcome, {user ? user.username : '...'}!</h1>
        <button onClick={onLogout}>Logout</button>
      </header>

      <main>
        <MeetingUploader token={token} />
        <div className="tasks-section">
          <h2>Your Action Items</h2>
          {tasks.length > 0 ? (
            <ul className="task-list">
              {tasks.map(task => (
                <li key={task.id}>
                  <strong>{task.description}</strong>
                  <span>(Due: {task.due_date_str}, Status: {task.status})</span>
                </li>
              ))}
            </ul>
          ) : (
            <p>You have no assigned tasks.</p>
          )}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;