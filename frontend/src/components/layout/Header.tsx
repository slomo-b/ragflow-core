import React from 'react';
import { Database, Activity, RefreshCw } from 'lucide-react';

interface HeaderProps {
  backendConnected: boolean;
  onRefresh: () => void;
}

export function Header({ backendConnected, onRefresh }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Database className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">RagFlow</h1>
            <p className="text-sm text-gray-500">Open Source RAG Platform</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Activity className={`w-4 h-4 ${backendConnected ? 'text-green-500' : 'text-red-500'}`} />
            <span>Backend: {backendConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <button 
            onClick={onRefresh}
            className="p-2 rounded-lg hover:bg-gray-100"
            title="Refresh connection"
          >
            <RefreshCw className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>
    </header>
  );
}
