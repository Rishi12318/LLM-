'use client';

import { useState, useCallback, useEffect } from 'react';
import { Upload, FileAudio, X, Loader2 } from 'lucide-react';

const API_URL = 'http://localhost:8000';

interface AudioUploaderProps {
  onUploadComplete: (jobId: string) => void;
  onResultsReady: (results: any) => void;
  currentJobId: string | null;
}

export default function AudioUploader({ 
  onUploadComplete, 
  onResultsReady,
  currentJobId 
}: AudioUploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Poll for job status
  useEffect(() => {
    if (!currentJobId || !processing) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/status/${currentJobId}`);
        const data = await response.json();

        setProgress(data.progress);
        setStatusMessage(data.message);

        if (data.status === 'completed') {
          setProcessing(false);
          onResultsReady(data.result);
        } else if (data.status === 'failed') {
          setProcessing(false);
          setError(data.message);
        }
      } catch (err) {
        console.error('Status check failed:', err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [currentJobId, processing, onResultsReady]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      validateAndSetFile(files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      validateAndSetFile(files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    const validTypes = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/m4a', 'audio/flac', 'audio/ogg'];
    const validExtensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.opus'];
    
    const isValidType = validTypes.includes(file.type) || 
                        validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

    if (!isValidType) {
      setError('Please upload a valid audio file (WAV, MP3, M4A, FLAC, OGG)');
      return;
    }

    if (file.size > 100 * 1024 * 1024) { // 100MB limit
      setError('File size must be less than 100MB');
      return;
    }

    setFile(file);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setProgress(0);
    setStatusMessage('Uploading file...');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('model', 'large-v3');
      formData.append('skip_diarization', 'true');

      const response = await fetch(`${API_URL}/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      
      setUploading(false);
      setProcessing(true);
      setProgress(10);
      setStatusMessage('Processing audio...');
      
      onUploadComplete(data.job_id);

    } catch (err) {
      setUploading(false);
      setError(err instanceof Error ? err.message : 'Upload failed');
    }
  };

  const handleReset = () => {
    setFile(null);
    setError(null);
    setProgress(0);
    setStatusMessage('');
    setProcessing(false);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
      {!file && !processing && (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-3 border-dashed rounded-xl p-12 text-center transition-all ${
            isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
        >
          <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <p className="text-xl font-semibold text-gray-700 mb-2">
            Drop your audio file here
          </p>
          <p className="text-gray-500 mb-6">
            or click to browse (WAV, MP3, M4A, FLAC, OGG)
          </p>
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".wav,.mp3,.m4a,.flac,.ogg,.opus,audio/*"
            onChange={handleFileInput}
          />
          <label
            htmlFor="file-upload"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold cursor-pointer hover:bg-blue-700 transition-colors"
          >
            Choose File
          </label>
          {error && (
            <p className="mt-4 text-red-600">{error}</p>
          )}
        </div>
      )}

      {file && !processing && (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center gap-3">
              <FileAudio className="w-8 h-8 text-blue-600" />
              <div>
                <p className="font-semibold text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={handleReset}
              className="text-gray-400 hover:text-red-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full bg-green-600 text-white py-4 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {uploading ? 'Uploading...' : 'Start Transcription'}
          </button>
        </div>
      )}

      {processing && (
        <div className="space-y-6">
          <div className="flex items-center justify-center">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
          </div>
          
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                {statusMessage}
              </span>
              <span className="text-sm font-medium text-blue-600">
                {progress}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          <p className="text-center text-gray-600">
            This may take a few minutes depending on file size...
          </p>
        </div>
      )}
    </div>
  );
}
