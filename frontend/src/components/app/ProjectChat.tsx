// File: frontend/src/components/app/ProjectChat.tsx
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, ArrowLeft, FileText, Settings, X } from 'lucide-react';
import { Project } from './MainApp';
import { Document, apiService } from '@/lib/api';

interface ProjectChatProps {
  chatId: string;
  project: Project;
  documents: Document[];
  onBack: () => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: any[];
  provider?: string;
  tokens?: number;
}

const ProjectChat: React.FC<ProjectChatProps> = ({ chatId, project, documents, onBack }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [providers, setProviders] = useState<string[]>(['gemini']);
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [showSettings, setShowSettings] = useState(false);
  const [chatName, setChatName] = useState(`Chat ${chatId}`);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchProviders();
    loadChatHistory();
    // Add welcome message for new chats
    if (messages.length === 0) {
      const availableDocs = documents.filter(d => d.status === 'completed');
      const welcomeMessage: Message = {
        id: '1',
        role: 'assistant',
        content: `Welcome to ${project.name}! I can help you with questions about your ${availableDocs.length} uploaded document${availableDocs.length !== 1 ? 's' : ''}. ${availableDocs.length === 0 ? 'Please upload some documents first to get started.' : 'What would you like to know?'}`,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [chatId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchProviders = async () => {
    try {
      const response = await apiService.getProviders();
      setProviders(response.providers || ['gemini']);
      if (response.default_provider) {
        setSelectedProvider(response.default_provider);
      }
    } catch (error) {
      console.error('Failed to fetch providers:', error);
    }
  };

  const loadChatHistory = () => {
    // TODO: Load chat history from API
    // For now, we'll start with empty messages (except welcome message)
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const availableDocs = documents.filter(d => d.status === 'completed');
    if (availableDocs.length === 0) {
      alert('Please upload and process some documents first before chatting.');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Use RAG chat with project documents
      const response = await apiService.chat({
        message: inputValue,
        provider: selectedProvider,
        max_tokens: 1000,
        temperature: 0.7,
        max_results: 5
        // In real implementation, we'd filter by project documents
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        sources: response.sources,
        provider: response.provider,
        tokens: response.tokens_used
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const availableDocuments = documents.filter(d => d.status === 'completed');
  const processingDocuments = documents.filter(d => d.status === 'processing');

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={onBack}
              className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            
            <div>
              <h1 className="text-xl font-semibold text-slate-800">{chatName}</h1>
              <p className="text-sm text-slate-500">
                {project.name} • {availableDocuments.length} docs ready
                {processingDocuments.length > 0 && ` • ${processingDocuments.length} processing`}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="mt-4 p-4 bg-slate-50 rounded-lg border">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-slate-700">Chat Settings</h3>
              <button
                onClick={() => setShowSettings(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">
                  Chat Name
                </label>
                <input
                  type="text"
                  value={chatName}
                  onChange={(e) => setChatName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">
                  LLM Provider
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {providers.map(provider => (
                    <option key={provider} value={provider}>
                      {provider.charAt(0).toUpperCase() + provider.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">
                  Available Documents ({availableDocuments.length})
                </label>
                <div className="max-h-32 overflow-y-auto bg-white border border-slate-300 rounded-md">
                  {availableDocuments.length > 0 ? (
                    availableDocuments.map((doc) => (
                      <div key={doc.id} className="flex items-center p-2 text-sm border-b border-slate-100 last:border-b-0">
                        <FileText className="w-4 h-4 text-green-500 mr-2" />
                        <span className="truncate">{doc.original_filename}</span>
                      </div>
                    ))
                  ) : (
                    <div className="p-3 text-sm text-slate-500 text-center">
                      No processed documents available
                    </div>
                  )}
                </div>
              </div>
              
              {processingDocuments.length > 0 && (
                <div className="text-xs text-slate-500 bg-blue-50 p-2 rounded">
                  💡 {processingDocuments.length} document{processingDocuments.length !== 1 ? 's' : ''} still processing. They'll be available for chat once completed.
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-slate-800 shadow-sm border border-slate-200'
              }`}
            >
              <div className="flex items-start space-x-2">
                <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
                  message.role === 'user' ? 'bg-blue-400' : 'bg-slate-100'
                }`}>
                  {message.role === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4 text-slate-600" />
                  )}
                </div>
                
                <div className="flex-1">
                  <div className="whitespace-pre-wrap break-words">
                    {message.content}
                  </div>
                  
                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <div className="text-xs font-medium text-slate-500">Sources from project documents:</div>
                      {message.sources.map((source, index) => (
                        <div key={index} className="text-xs p-2 bg-slate-50 rounded border-l-2 border-purple-200">
                          <div className="font-medium text-slate-600">
                            📄 {source.document_filename}
                          </div>
                          <div className="text-slate-500 mt-1 line-clamp-2">
                            {source.text.substring(0, 100)}...
                          </div>
                          <div className="text-slate-400 mt-1">
                            Relevance: {(source.score * 100).toFixed(1)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Metadata */}
                  <div className="flex items-center justify-between mt-2 text-xs opacity-70">
                    <span>{message.timestamp.toLocaleTimeString()}</span>
                    <div className="flex items-center space-x-2">
                      {message.provider && (
                        <span>via {message.provider}</span>
                      )}
                      {message.tokens && (
                        <span>{message.tokens} tokens</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white text-slate-800 shadow-sm border border-slate-200 rounded-2xl px-4 py-3">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-purple-500" />
                <span className="text-sm">Searching through your documents...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-slate-200 px-6 py-4">
        {availableDocuments.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-slate-500 mb-2">No documents available for chat.</p>
            <button
              onClick={onBack}
              className="text-blue-500 hover:text-blue-600 text-sm"
            >
              Go back to upload documents
            </button>
          </div>
        ) : (
          <div className="flex items-end space-x-3">
            {/* Text Input */}
            <div className="flex-1 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Ask questions about your ${availableDocuments.length} document${availableDocuments.length !== 1 ? 's' : ''} in ${project.name}...`}
                className="w-full px-4 py-3 border border-slate-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                rows={inputValue.split('\n').length}
                style={{ minHeight: '48px', maxHeight: '120px' }}
              />
            </div>
            
            {/* Send Button */}
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading || availableDocuments.length === 0}
              className="flex-shrink-0 p-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectChat;