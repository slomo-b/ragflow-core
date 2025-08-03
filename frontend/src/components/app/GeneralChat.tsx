// File: frontend/src/components/app/GeneralChat.tsx
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Settings, X, Plus } from 'lucide-react';
import { apiService } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  provider?: string;
  tokens?: number;
}

const GeneralChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [providers, setProviders] = useState<string[]>(['gemini']);
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [showSettings, setShowSettings] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchProviders();
    // Add welcome message
    setMessages([{
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI assistant. I can help you with general questions and conversations. For document-specific queries, create a project and upload your documents there.',
      timestamp: new Date()
    }]);
  }, []);

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

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

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
      // Use simple chat (no document context)
      const response = await apiService.simpleChat({
        message: inputValue,
        provider: selectedProvider,
        max_tokens: 1000,
        temperature: 0.7
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
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

  const clearChat = () => {
    setMessages([{
      id: '1',
      role: 'assistant',
      content: 'Chat cleared! How can I help you today?',
      timestamp: new Date()
    }]);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-600 rounded-lg flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-slate-800">General Chat</h1>
              <p className="text-sm text-slate-500">
                Chat without document context • Provider: {selectedProvider}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={clearChat}
              className="px-3 py-1 text-sm text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded transition-colors"
            >
              Clear Chat
            </button>
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
              
              <div className="text-xs text-slate-500">
                <p>💡 For document-based conversations, create a project and upload your files there.</p>
              </div>
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
                <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                <span className="text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-slate-200 px-6 py-4">
        <div className="flex items-end space-x-3">
          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              className="w-full px-4 py-3 border border-slate-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={inputValue.split('\n').length}
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
          </div>
          
          {/* Send Button */}
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="flex-shrink-0 p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default GeneralChat;