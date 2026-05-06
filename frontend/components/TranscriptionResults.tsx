'use client';

import { useState } from 'react';
import { Download, FileJson, FileText, Languages, User, Clock, ChevronDown, ChevronUp } from 'lucide-react';

interface Segment {
  speaker: string;
  start: number;
  end: number;
  original: string;
  english?: string;
}

interface TranscriptionResultsProps {
  results: {
    language: string;
    duration: number;
    speakers: number;
    segments: Segment[];
    files: Record<string, string>;
  };
  jobId: string | null;
}

export default function TranscriptionResults({ results, jobId }: TranscriptionResultsProps) {
  const [expanded, setExpanded] = useState(true);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const downloadFile = (url: string, filename: string) => {
    const fullUrl = `http://localhost:8000/api${url}`;
    window.open(fullUrl, '_blank');
  };

  return (
    <div className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-[2.5rem] overflow-hidden shadow-2xl transition-all">
      {/* Header */}
      <div className="p-8 border-b border-white/10 flex flex-wrap items-center justify-between gap-6 bg-white/[0.02]">
        <div>
          <h2 className="text-2xl font-bold mb-2 flex items-center gap-2 text-white">
            <Languages className="w-6 h-6 text-indigo-500" />
            Transcription Analysis
          </h2>
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-gray-400">
              <Languages className="w-3.5 h-3.5" /> Language: <span className="text-white font-bold uppercase">{results.language}</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-gray-400">
              <Clock className="w-3.5 h-3.5" /> Duration: <span className="text-white font-bold">{results.duration}s</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-gray-400">
              <User className="w-3.5 h-3.5" /> Speakers: <span className="text-white font-bold">{results.speakers}</span>
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <button 
            onClick={() => downloadFile(results.files.json, 'result.json')}
            className="p-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-gray-300 hover:text-white"
            title="Download JSON"
          >
            <FileJson className="w-5 h-5" />
          </button>
          <button 
            onClick={() => downloadFile(results.files.text, 'result.txt')}
            className="p-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-gray-300 hover:text-white"
            title="Download TXT"
          >
            <FileText className="w-5 h-5" />
          </button>
          <button 
            onClick={() => setExpanded(!expanded)}
            className="p-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 transition-all text-white flex items-center gap-2 font-bold px-5"
          >
            {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            {expanded ? "Hide Details" : "View Details"}
          </button>
        </div>
      </div>

      {/* Segments List */}
      {expanded && (
        <div className="p-8 max-h-[800px] overflow-y-auto space-y-6 custom-scrollbar">
          {results.segments.map((segment, index) => (
            <div 
              key={index} 
              className="group flex gap-6 p-6 rounded-3xl bg-white/[0.03] border border-white/5 hover:border-indigo-500/30 hover:bg-white/[0.05] transition-all"
            >
              <div className="flex-shrink-0 flex flex-col items-center">
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-2 ${
                  segment.speaker.includes('1') ? 'bg-indigo-500/20 text-indigo-400' : 'bg-purple-500/20 text-purple-400'
                }`}>
                  <User className="w-6 h-6" />
                </div>
                <span className="text-[10px] font-black uppercase tracking-widest text-gray-500">{segment.speaker}</span>
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-white/10 text-gray-400">
                    {formatTime(segment.start)} - {formatTime(segment.end)}
                  </span>
                </div>
                
                <p className="text-white text-lg leading-relaxed mb-3">
                  {segment.original}
                </p>

                {segment.english && segment.english !== segment.original && (
                  <div className="pl-4 border-l-2 border-indigo-500/30 mt-2">
                    <p className="text-gray-400 text-base italic leading-relaxed">
                      {segment.english}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
