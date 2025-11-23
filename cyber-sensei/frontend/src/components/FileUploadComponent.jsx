import React, { useState, useRef } from 'react';
import './FileUploadComponent.css';

/**
 * Advanced File Upload Component with drag-and-drop and batch processing.
 * Features:
 * - Drag and drop support
 * - Multiple file selection
 * - Progress tracking per file
 * - File validation
 * - Batch operations
 * - Preview for supported formats
 */
const FileUploadComponent = ({ topicId, onUploadComplete }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState({});
  const [errors, setErrors] = useState({});
  const dragRef = useRef(null);

  // Supported file types
  const SUPPORTED_TYPES = {
    'video': ['mp4', 'webm', 'mov'],
    'pdf': ['pdf'],
    'article': ['doc', 'docx', 'txt'],
    'code': ['py', 'js', 'java', 'cpp']
  };

  const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
  const MAX_FILES = 10;

  /**
   * Detect file type from extension
   */
  const detectFileType = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();

    for (const [type, extensions] of Object.entries(SUPPORTED_TYPES)) {
      if (extensions.includes(ext)) {
        return type;
      }
    }
    return 'article'; // Default type
  };

  /**
   * Validate file before adding to queue
   */
  const validateFile = (file) => {
    const errors = [];

    if (file.size > MAX_FILE_SIZE) {
      errors.push(`File size exceeds ${MAX_FILE_SIZE / 1024 / 1024}MB limit`);
    }

    const type = detectFileType(file.name);
    if (!type) {
      errors.push('File type not supported');
    }

    return errors;
  };

  /**
   * Handle file selection from input
   */
  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    handleFiles(selectedFiles);
  };

  /**
   * Handle dropped files
   */
  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();

    dragRef.current?.classList.remove('drag-over');

    const droppedFiles = Array.from(event.dataTransfer.files);
    handleFiles(droppedFiles);
  };

  /**
   * Process selected/dropped files
   */
  const handleFiles = (selectedFiles) => {
    if (selectedFiles.length + files.length > MAX_FILES) {
      alert(`Maximum ${MAX_FILES} files allowed`);
      return;
    }

    const newFiles = selectedFiles.map((file, index) => ({
      id: `${Date.now()}-${index}`,
      file,
      name: file.name,
      size: file.size,
      type: detectFileType(file.name),
      status: 'pending',
      progress: 0,
      error: null
    }));

    // Validate files
    const validationErrors = {};
    newFiles.forEach(f => {
      const fileErrors = validateFile(f.file);
      if (fileErrors.length > 0) {
        f.status = 'error';
        validationErrors[f.id] = fileErrors;
      }
    });

    setFiles([...files, ...newFiles]);
    setErrors(validationErrors);
  };

  /**
   * Upload single file with progress tracking
   */
  const uploadFile = async (fileObj) => {
    const formData = new FormData();
    formData.append('file', fileObj.file);
    formData.append('topic_id', topicId);
    formData.append('resource_type', fileObj.type);

    try {
      const xhr = new XMLHttpRequest();

      // Track upload progress
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded / event.total) * 100);
          setProgress(prev => ({
            ...prev,
            [fileObj.id]: percentComplete
          }));
        }
      });

      // Handle completion
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          updateFileStatus(fileObj.id, 'completed');
        } else {
          updateFileStatus(fileObj.id, 'error', 'Upload failed');
        }
      });

      // Handle error
      xhr.addEventListener('error', () => {
        updateFileStatus(fileObj.id, 'error', 'Network error');
      });

      xhr.open('POST', '/api/upload', true);
      xhr.setRequestHeader('Authorization', `Bearer ${localStorage.getItem('token')}`);
      xhr.send(formData);
    } catch (error) {
      updateFileStatus(fileObj.id, 'error', error.message);
    }
  };

  /**
   * Update file status
   */
  const updateFileStatus = (fileId, status, error = null) => {
    setFiles(prevFiles =>
      prevFiles.map(f =>
        f.id === fileId ? { ...f, status, error } : f
      )
    );
  };

  /**
   * Start uploading all pending files
   */
  const handleUploadAll = async () => {
    const pendingFiles = files.filter(f => f.status === 'pending');

    if (pendingFiles.length === 0) {
      alert('No files to upload');
      return;
    }

    setUploading(true);

    // Upload files in parallel (max 3 concurrent)
    const uploadQueue = [...pendingFiles];
    const concurrency = 3;

    const uploadBatch = async (batch) => {
      await Promise.all(batch.map(f => uploadFile(f)));
    };

    for (let i = 0; i < uploadQueue.length; i += concurrency) {
      await uploadBatch(uploadQueue.slice(i, i + concurrency));
    }

    setUploading(false);

    // Call completion callback
    const completedFiles = files.filter(f => f.status === 'completed');
    if (completedFiles.length > 0) {
      onUploadComplete?.(completedFiles);
    }
  };

  /**
   * Remove file from queue
   */
  const removeFile = (fileId) => {
    setFiles(files.filter(f => f.id !== fileId));
    const newErrors = { ...errors };
    delete newErrors[fileId];
    setErrors(newErrors);
  };

  /**
   * Get status icon
   */
  const getStatusIcon = (status) => {
    const icons = {
      pending: '⏳',
      uploading: '📤',
      completed: '✅',
      error: '❌'
    };
    return icons[status] || '📄';
  };

  /**
   * Format file size for display
   */
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="file-upload-container">
      <h2>Upload Learning Materials</h2>

      {/* Drag and Drop Area */}
      <div
        className="drop-zone"
        ref={dragRef}
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          dragRef.current?.classList.add('drag-over');
        }}
        onDragLeave={() => dragRef.current?.classList.remove('drag-over')}
      >
        <div className="drop-zone-content">
          <span className="drop-icon">📁</span>
          <p className="drop-text">Drag and drop files here</p>
          <p className="drop-subtext">or click to browse</p>
          <input
            type="file"
            multiple
            onChange={handleFileSelect}
            className="file-input"
            accept=".mp4,.webm,.mov,.pdf,.doc,.docx,.txt,.py,.js,.java,.cpp"
          />
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="file-list">
          <h3>Files to Upload ({files.length}/{MAX_FILES})</h3>

          {files.map(fileObj => (
            <div key={fileObj.id} className={`file-item file-${fileObj.status}`}>
              <div className="file-header">
                <span className="file-status">{getStatusIcon(fileObj.status)}</span>
                <div className="file-info">
                  <p className="file-name">{fileObj.name}</p>
                  <p className="file-size">{formatFileSize(fileObj.size)}</p>
                  {fileObj.error && <p className="file-error">{fileObj.error}</p>}
                </div>
                <span className="file-type">{fileObj.type}</span>
              </div>

              {/* Progress Bar */}
              {(fileObj.status === 'uploading' || fileObj.status === 'pending') && (
                <div className="file-progress">
                  <div className="progress-bar-wrapper">
                    <div
                      className="progress-bar"
                      style={{ width: `${progress[fileObj.id] || 0}%` }}
                    />
                  </div>
                  <span className="progress-text">{progress[fileObj.id] || 0}%</span>
                </div>
              )}

              {/* Remove Button */}
              {fileObj.status !== 'uploading' && (
                <button
                  className="btn-remove"
                  onClick={() => removeFile(fileObj.id)}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Action Buttons */}
      {files.length > 0 && (
        <div className="upload-actions">
          <button
            className="btn-upload"
            onClick={handleUploadAll}
            disabled={uploading || files.every(f => f.status !== 'pending')}
          >
            {uploading ? 'Uploading...' : `Upload ${files.filter(f => f.status === 'pending').length} Files`}
          </button>
          <p className="upload-info">
            Max file size: {MAX_FILE_SIZE / 1024 / 1024}MB | Supported: Video, PDF, Documents, Code
          </p>
        </div>
      )}
    </div>
  );
};

export default FileUploadComponent;
