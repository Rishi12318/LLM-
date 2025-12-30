'use client';

import { useState } from 'react';
import AudioUploader from '@/components/AudioUploader';
import TranscriptionResults from '@/components/TranscriptionResults';

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);

  const handleUploadComplete = (newJobId: string) => {
    setJobId(newJobId);
    setResults(null);
  };

  const handleResultsReady = (data: any) => {
    setResults(data);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🎙️ Multilingual Audio Transcriber
          </h1>
          <p className="text-xl text-gray-600">
            Upload audio, get transcription & translation in 100+ languages
          </p>
          <div className="mt-4 flex justify-center gap-4 text-sm text-gray-500">
            <span>✓ Auto Language Detection</span>
            <span>✓ Speaker Diarization</span>
            <span>✓ English Translation</span>
            <span>✓ Multiple Formats</span>
          </div>
        </div>

        {/* Uploader */}
        <AudioUploader 
          onUploadComplete={handleUploadComplete}
          onResultsReady={handleResultsReady}
          currentJobId={jobId}
        />

        {/* Results */}
        {results && (
          <TranscriptionResults 
            results={results}
            jobId={jobId}
          />
        )}
      </div>
    </main>
  );
}
