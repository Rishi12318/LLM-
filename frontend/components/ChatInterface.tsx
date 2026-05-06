'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, RefreshCw, Quote } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  retrieval?: any[];
}

interface ChatInterfaceProps {
  jobId: string;
}

export default function ChatInterface({ jobId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Construct history for the backend
      const history = messages.map(m => ({
        role: m.role,
        content: m.content
      }));

      const response = await fetch('http://localhost:8000/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          history: history,
          use_llm: true
        })
      });

      if (!response.ok) throw new Error('Failed to query AI');
      
      const data = await response.json();
      
      const assistantMsg: Message = {
        role: 'assistant',
        content: data.answer,
        retrieval: data.retrieval
      };
      
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "Sorry, I encountered an error while processing your request. Please ensure the backend and Ollama are running." 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 flex flex-col h-[600px] overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between bg-gray-50/50 dark:bg-gray-800/50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white leading-tight">Conversation Assistant</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">Ask anything about the transcript</p>
          </div>
        </div>
        <button 
          onClick={() => setMessages([])}
          className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
          title="Clear chat"
        >
          <RefreshCw className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {/* Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
      >
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-50">
            <Bot className="w-12 h-12 mb-4 text-indigo-500" />
            <p className="text-gray-600 dark:text-gray-400">
              Hello! I've analyzed the transcription. <br />
              Ask me for details, summaries, or specific timestamps.
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div 
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[85%] flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
                msg.role === 'user' ? 'bg-indigo-100 dark:bg-indigo-900' : 'bg-gray-100 dark:bg-gray-800'
              }`}>
                {msg.role === 'user' ? <User className="w-4 h-4 text-indigo-600" /> : <Bot className="w-4 h-4 text-gray-600" />}
              </div>
              
              <div className={`rounded-2xl p-4 ${
                msg.role === 'user' 
                  ? 'bg-indigo-600 text-white rounded-tr-none' 
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none'
              }`}>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                
                {msg.retrieval && msg.retrieval.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200/50 dark:border-gray-700/50">
                    <p className="text-[10px] font-bold uppercase tracking-wider opacity-50 mb-2 flex items-center gap-1">
                      <Quote className="w-3 h-3" /> Sources
                    </p>
                    <div className="space-y-2">
                      {msg.retrieval.slice(0, 2).map((hit, hIdx) => (
                        <div key={hIdx} className="text-[11px] bg-white/10 p-2 rounded border border-white/10">
                          <span className="font-bold block mb-1 opacity-70 italic">[{hit.source}]</span>
                          "{hit.text.substring(0, 100)}..."
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex gap-3 max-w-[85%] items-end">
              <div className="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                <Bot className="w-4 h-4 text-gray-600" />
              </div>
              <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-none p-4">
                <Loader2 className="w-5 h-5 text-indigo-500 animate-spin" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about the conversation..."
            className="w-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl py-3 pl-4 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all shadow-sm"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white rounded-lg transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-[10px] text-center mt-2 text-gray-400">
          Powered by Gemini Retrieval-Augmented Generation
        </p>
      </div>
    </div>
  );
}
