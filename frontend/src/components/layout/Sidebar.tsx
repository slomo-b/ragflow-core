import React from 'react';
import { Upload, Search, Settings } from 'lucide-react';
import { TabType } from '@/components/dashboard/RagFlowDashboard';
import { Document } from '@/types/document';

interface SidebarProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  documents: Document[];
}

export function Sidebar({ activeTab, onTabChange, documents }: SidebarProps) {
  const completedCount = documents.filter(d => d.status === 'completed').length;
  const processingCount = documents.filter(d => d.status === 'processing').length;

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <nav className="p-4">
        <div className="space-y-2">
          <button
            onClick={() => onTabChange('upload')}
            className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
              activeTab === 'upload' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Upload className="w-5 h-5" />
            <span>Upload Documents</span>
          </button>
          
          <button
            onClick={() => onTabChange('search')}
            className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
              activeTab === 'search' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Search className="w-5 h-5" />
            <span>Search Documents</span>
          </button>
          
          <button
            onClick={() => onTabChange('admin')}
            className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
              activeTab === 'admin' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Settings className="w-5 h-5" />
            <span>Admin Dashboard</span>
          </button>
        </div>
      </nav>

      {/* Document Stats */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-sm text-gray-600">
          <div className="flex justify-between">
            <span>Total Documents:</span>
            <span className="font-medium">{documents.length}</span>
          </div>
          <div className="flex justify-between mt-1">
            <span>Processed:</span>
            <span className="font-medium text-green-600">{completedCount}</span>
          </div>
          <div className="flex justify-between mt-1">
            <span>Processing:</span>
            <span className="font-medium text-blue-600">{processingCount}</span>
          </div>
        </div>
      </div>
    </div>
  );
}