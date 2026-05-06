'use client';

import { useState } from 'react';
import { Mic, Globe, Cpu, Layers, Github, Terminal } from 'lucide-react';
import AudioUploader from '@/components/AudioUploader';
import TranscriptionResults from '@/components/TranscriptionResults';
import ChatInterface from '@/components/ChatInterface';
import SummaryCard from '@/components/SummaryCard';

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
    <div className="min-h-screen bg-[#0a0a0b] text-gray-100 selection:bg-indigo-500/30">
      {/* Dynamic Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-900/20 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-900/20 blur-[120px]" />
      </div>

      <main className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-center mb-16 gap-8">
          <div className="text-center md:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold uppercase tracking-widest mb-6">
              <Terminal className="w-3 h-3" /> Industry-Grade AI System
            </div>
            <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-4 bg-gradient-to-r from-white via-gray-200 to-gray-500 bg-clip-text text-transparent">
              TRANSCRIPT.<span className="text-indigo-500">AI</span>
            </h1>
            <p className="text-lg text-gray-400 max-w-xl font-medium leading-relaxed">
              Professional conversational transcription system powered by <span className="text-white">OpenAI Whisper</span>, 
              <span className="text-white"> RAG</span> pipelines, and <span className="text-white">LLM summarization</span>.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 w-full md:w-auto">
            {[
              { icon: Mic, text: "Multi-Format STT" },
              { icon: Globe, text: "100+ Languages" },
              { icon: Cpu, text: "GPU Accelerated" },
              { icon: Layers, text: "RAG & Search" },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-2 p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm">
                <item.icon className="w-5 h-5 text-indigo-500" />
                <span className="text-xs font-bold text-gray-300">{item.text}</span>
              </div>
            ))}
          </div>
        </header>

        {/* Action Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Upload & Transcribe */}
          <div className="lg:col-span-5 space-y-8">
            <div className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-[2.5rem] p-1 shadow-2xl">
              <AudioUploader 
                onUploadComplete={handleUploadComplete}
                onResultsReady={handleResultsReady}
                currentJobId={jobId}
              />
            </div>
            
            {results && <SummaryCard jobId={jobId!} />}
            
            <div className="p-6 rounded-3xl bg-gradient-to-br from-indigo-600/10 to-purple-600/10 border border-indigo-500/20">
              <h3 className="font-bold mb-2 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-indigo-400" /> System Architecture
              </h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Modular pipeline featuring FAISS vector store, sentence-transformer embeddings, 
                and context-aware memory for human-like conversational querying.
              </p>
            </div>
          </div>

          {/* Right Column: Chat & Results */}
          <div className="lg:col-span-7 space-y-8">
            {jobId && results ? (
              <>
                <ChatInterface jobId={jobId} />
                <TranscriptionResults results={results} jobId={jobId} />
              </>
            ) : (
              <div className="h-full min-h-[600px] flex flex-col items-center justify-center border-2 border-dashed border-white/5 rounded-[2.5rem] bg-white/[0.02] p-12 text-center opacity-40">
                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6">
                  <Mic className="w-10 h-10 text-gray-400" />
                </div>
                <h3 className="text-2xl font-bold mb-2">Awaiting Transcription</h3>
                <p className="text-gray-400 max-w-sm">
                  Upload an audio file to begin the AI analysis and unlock the conversational interface.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-24 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4 text-gray-500 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            System Status: Operational
          </div>
          <div className="flex items-center gap-6">
            <a href="#" className="hover:text-white transition-colors flex items-center gap-2">
              <Github className="w-4 h-4" /> Source
            </a>
            <span className="opacity-20">|</span>
            <span>&copy; 2026 AI Transcription Engine</span>
          </div>
        </footer>
      </main>
    </div>
  );
}
