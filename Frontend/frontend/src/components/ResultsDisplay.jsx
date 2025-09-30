import React from 'react';

function ResultsDisplay({ result }) {
  if (!result) return null;

  const { minutes, tasks } = result.results;

  return (
    <div className="results-container">
      <h2>📝 Minutes of Meeting</h2>
      <p className="summary">{minutes || "No summary was generated."}</p>

      <h2>📌 Action Items</h2>
      {tasks && tasks.length > 0 ? (
        <ul className="task-list">
          {tasks.map((task, index) => (
            <li key={index}>
              <strong>{task.task_description}</strong>
              <span>(Assignee: {task.assignee}, Due: {task.due_date})</span>
            </li>
          ))}
        </ul>
      ) : (
        <p>No action items were identified.</p>
      )}
    </div>
  );
}

export default ResultsDisplay;