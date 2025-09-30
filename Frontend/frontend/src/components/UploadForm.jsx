import React from 'react';

function UploadForm({ onFileSelect, onSubmit, isLoading }) {
  return (
    <form className="upload-form" onSubmit={onSubmit}>
      <input 
        type="file" 
        onChange={(e) => onFileSelect(e.target.files[0])} 
        accept="audio/*" 
      />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Analyzing...' : 'Analyze Meeting'}
      </button>
    </form>
  );
}

export default UploadForm;