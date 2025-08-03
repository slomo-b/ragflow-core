// File: frontend/src/components/app/ProjectView.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  FileText, 
  MessageSquare, 
  Plus, 
  Trash2, 
  Settings,
  CheckCircle,
  AlertCircle,
  Loader2,
  Bot,
  FolderOpen
} from 'lucide-react';
import { Project } from './MainApp';
import { apiService, Document } from '@/lib/api';
import ProjectChat from './ProjectChat';

interface ProjectViewProps {
  project: Project;
  onProjectUpdate: (project: Project) => void;
}

type TabType = 'overview' | 'documents' | 'chats';

const ProjectView: React.FC<ProjectViewProps> = ({ project, onProjectUpdate }) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [projectChats, setProjectChats] = useState<any[]>([]);

  useEffect(() => {
    fetchDocuments();
    fetchProjectChats();
  }, [project.id]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await apiService.getDocuments(0, 100); // Updated to match API
      setDocuments(response.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjectChats = () => {
    // Mock project chats - in real app, this would be an API call
    const mockChats = [
      {
        id: '1',
        name: 'Research Discussion',
        projectId: project.id,
        lastMessage: 'What are the main findings?',
        updatedAt: new Date(),
        messageCount: 15
      },
      {
        id: '2', 
        name: 'Summary Chat',
        projectId: project.id,
        lastMessage: 'Can you summarize the key points?',
        updatedAt: new Date(),
        messageCount: 8
      }
    ];
    setProjectChats(mockChats);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);

    try {
      for (const file of Array.from(files)) {
        await apiService.uploadDocument(file);
      }
      await fetchDocuments();
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  const createNewChat = () => {
    const newChat = {
      id: Date.now().toString(),
      name: `Chat ${projectChats.length + 1}`,
      projectId: project.id,
      lastMessage: '',
      updatedAt: new Date(),
      messageCount: 0
    };
    setProjectChats(prev => [...prev, newChat]);
    setSelectedChatId(newChat.id);
    setActiveTab('chats');
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Loader2 className="w-4 h-4 text-gray-500 animate-spin" />;
    }
  };

  const getFileTypeIcon = (contentType: string) => {
    if (contentType.includes('pdf')) return '📄';
    if (contentType.includes('word')) return '📝';
    if (contentType.includes('text')) return '📃';
    if (contentType.includes('html')) return '🌐';
    if (contentType.includes('markdown')) return '📑';
    return '📄';
  };

  if (selectedChatId) {
    return (
      <ProjectChat 
        chatId={selectedChatId}
        project={project}
        documents={documents}
        onBack={() => setSelectedChatId(null)}
      />
    );
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
              <FolderOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-800">{project.name}</h1>
              <p className="text-sm text-gray-500">{project.description}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={createNewChat}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>New Chat</span>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-6 mt-4">
          {[
            { id: 'overview', label: 'Overview', icon: Settings },
            { id: 'documents', label: 'Documents', icon: FileText },
            { id: 'chats', label: 'Chats', icon: MessageSquare }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`flex items-center space-x-2 px-3 py-2 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                {tab.id === 'documents' && (
                  <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                    {documents.length}
                  </span>
                )}
                {tab.id === 'chats' && (
                  <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                    {projectChats.length}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Project Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="w-8 h-8 text-blue-500" />
                  <div>
                    <div className="text-2xl font-bold text-blue-600">{documents.length}</div>
                    <div className="text-sm text-blue-600">Documents</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center space-x-3">
                  <MessageSquare className="w-8 h-8 text-green-500" />
                  <div>
                    <div className="text-2xl font-bold text-green-600">{projectChats.length}</div>
                    <div className="text-sm text-green-600">Chats</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-8 h-8 text-purple-500" />
                  <div>
                    <div className="text-2xl font-bold text-purple-600">
                      {documents.filter(d => d.status === 'completed').length}
                    </div>
                    <div className="text-sm text-purple-600">Processed</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3 text-sm">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>Project created</span>
                  <span className="text-gray-500">{project.createdAt.toLocaleDateString()}</span>
                </div>
                {documents.slice(0, 3).map(doc => (
                  <div key={doc.id} className="flex items-center space-x-3 text-sm">
                    <FileText className="w-4 h-4 text-blue-500" />
                    <span>Document uploaded: {doc.filename}</span>
                    <span className="text-gray-500">{new Date(doc.created_at).toLocaleDateString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="space-y-6">
            {/* Upload Area */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
              <input
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.md,.html"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
                disabled={uploading}
              />
              <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
                <Upload className="w-12 h-12 text-gray-400 mb-4" />
                <span className="text-lg font-medium text-gray-600 mb-2">
                  {uploading ? 'Uploading...' : 'Upload Documents'}
                </span>
                <span className="text-sm text-gray-500">
                  PDF, DOCX, TXT, MD, HTML files supported
                </span>
              </label>
            </div>

            {/* Documents List */}
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                <span className="ml-2 text-gray-600">Loading documents...</span>
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-600 mb-2">No documents uploaded</h3>
                <p className="text-gray-500">Upload your first document to get started</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {documents.map(doc => (
                  <div key={doc.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="text-2xl">
                          {getFileTypeIcon(doc.content_type)}
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">{doc.original_filename}</h4>
                          <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                            <span>{formatFileSize(doc.file_size)}</span>
                            <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                            {doc.chunks_count && (
                              <span>{doc.chunks_count} chunks</span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <button
                          onClick={async () => {
                            try {
                              await apiService.deleteDocument(doc.id);
                              await fetchDocuments(); // Refresh list
                            } catch (error) {
                              console.error('Delete failed:', error);
                            }
                          }}
                          className="p-2 text-gray-400 hover:text-red-500 rounded"
                          title="Delete document"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'chats' && (
          <div className="space-y-4">
            {projectChats.length === 0 ? (
              <div className="text-center py-12">
                <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-600 mb-2">No chats yet</h3>
                <p className="text-gray-500 mb-4">Start a conversation with your documents</p>
                <button
                  onClick={createNewChat}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors mx-auto"
                >
                  <Plus className="w-4 h-4" />
                  <span>Create First Chat</span>
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {projectChats.map(chat => (
                  <div 
                    key={chat.id} 
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => setSelectedChatId(chat.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <MessageSquare className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">{chat.name}</h4>
                          <p className="text-sm text-gray-500">{chat.lastMessage || 'No messages yet'}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-500">{chat.updatedAt.toLocaleDateString()}</div>
                        <div className="text-xs text-gray-400">{chat.messageCount} messages</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectView;