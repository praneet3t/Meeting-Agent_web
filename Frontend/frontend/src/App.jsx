import { useState } from 'react';
import axios from 'axios';
import UploadForm from './components/UploadForm';
import ResultsDisplay from './components/ResultsDisplay';
import './App.css'; // We'll add styles next

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // The URL of your running FastAPI backend
  const API_URL = 'http://127.0.0.1:8000/process-audio/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file first!');
      return;
    }

    setIsLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(API_URL, formData);
      setResult(response.data);
    } catch (err) {
      setError('An error occurred. Please check the backend and try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>Meeting Analyzer 🤖</h1>
        <p>Upload your meeting audio to get a summary and actionable tasks.</p>
      </header>

      <main>
        <UploadForm 
          onFileSelect={setFile}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
        {error && <p className="error-message">{error}</p>}
        {isLoading && <p className="loading-message">Processing your meeting... this may take a moment.</p>}
        <ResultsDisplay result={result} />
      </main>
    </div>
  );
}

export default App;