import { useState, useEffect } from 'react';
import LoginPage from './LoginPage';
import Dashboard from './Dashboard';
import './App.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('userToken') || null);

  const handleLoginSuccess = (newToken) => {
    localStorage.setItem('userToken', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('userToken');
    setToken(null);
  };

  return (
    <div className="App">
      {token ? (
        <Dashboard token={token} onLogout={handleLogout} />
      ) : (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;