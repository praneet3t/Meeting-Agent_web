import { useState, useEffect } from 'react';
import axios from 'axios';

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
        console.error("Failed to fetch user data", error);
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
        {/* You can add your meeting upload component here */}
      </main>
    </div>
  );
}

export default Dashboard;