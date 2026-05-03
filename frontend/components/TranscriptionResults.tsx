'use client';

import { Download, FileText, FileJson } from 'lucide-react';

const API_URL = 'http://localhost:8000';

interface TranscriptionResultsProps {
  results: any;
  jobId: string | null;
}

const LANGUAGE_NAMES: { [key: string]: string } = {
  en: 'English', hi: 'Hindi', es: 'Spanish', fr: 'French',
  de: 'German', it: 'Italian', pt: 'Portuguese', ru: 'Russian',
  ja: 'Japanese', ko: 'Korean', zh: 'Chinese', ar: 'Arabic',
};

export default function TranscriptionResults({ results, jobId }: TranscriptionResultsProps) {
  const languageName = LANGUAGE_NAMES[results.language] || results.language.toUpperCase();

  const handleDownload = (type: string) => {
    const urls: { [key: string]: string } = {
      json: `${API_URL}/results/${jobId}/result.json`,
      markdown: `${API_URL}/results/${jobId}/result.md`,
      text: `${API_URL}/results/${jobId}/result.txt`,
      srt: `${API_URL}/results/${jobId}/result_original.srt`,
    };

    const link = document.createElement('a');
    link.href = urls[type];
    link.download = `transcription.${type === 'markdown' ? 'md' : type}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold text-gray-900">Results</h2>
        <div className="flex gap-2">
          <button
            onClick={() => handleDownload('json')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
          >
            <FileJson className="w-4 h-4" />
            JSON
          </button>
          <button
            onClick={() => handleDownload('markdown')}
            className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
          >
            <FileText className="w-4 h-4" />
            Markdown
          </button>
          <button
            onClick={() => handleDownload('text')}
            className="flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
          >
            <Download className="w-4 h-4" />
            Text
          </button>
          <button
            onClick={() => handleDownload('srt')}
            className="flex items-center gap-2 px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors"
          >
            <Download className="w-4 h-4" />
            SRT
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Language</p>
          <p className="text-2xl font-bold text-blue-600">{languageName}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Duration</p>
          <p className="text-2xl font-bold text-green-600">{results.duration}s</p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Speakers</p>
          <p className="text-2xl font-bold text-purple-600">{results.speakers}</p>
        </div>
      </div>

      {/* Transcript */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Transcript</h3>
        
        {results.segments && results.segments.map((segment: any, index: number) => (
          <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-sm font-semibold text-blue-600">
                {segment.speaker}
              </span>
              <span className="text-xs text-gray-500">
                {formatTime(segment.start)} - {formatTime(segment.end)}
              </span>
            </div>
            <p className="text-gray-800 mb-2 font-medium">{segment.original}</p>
            {segment.english && (
              <div className="bg-blue-50 px-3 py-2 rounded-md border-l-2 border-blue-400">
                <p className="text-sm text-gray-500 mb-1">🌐 English Translation:</p>
                <p className="text-gray-700">{segment.english}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}
