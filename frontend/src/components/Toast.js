import React, { useEffect } from 'react';
import './Toast.css';

function Toast({ message, type = 'success', isHtml = false, onClose, duration = 3000 }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [onClose, duration]);

  return (
    <div className={`toast toast-${type}`}>
      <div className="toast-content">
        {type === 'success' && <span className="toast-icon">✓</span>}
        {type === 'info' && <span className="toast-icon">ℹ</span>}
        {type === 'warning' && <span className="toast-icon">⚠</span>}
        {type === 'error' && <span className="toast-icon">✕</span>}
        {isHtml ? (
          <span className="toast-message" dangerouslySetInnerHTML={{ __html: message }} />
        ) : (
          <span className="toast-message">{message}</span>
        )}
      </div>
      <button className="toast-close" onClick={onClose}>×</button>
    </div>
  );
}

export default Toast;
