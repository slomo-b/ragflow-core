// File: frontend/src/components/app/MainApp.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, 
  FolderOpen, 
  Plus,
  Settings,
  Bot,
  Search,
  Activity,
  ChevronDown,
  ChevronRight,
  Trash2,
  Edit3
} from 'lucide-react';
import GeneralChat from './GeneralChat';
import ProjectView from './ProjectView';
import SystemStatus from './SystemStatus';

export interface Project {
  id: string;
  name: string;
  description: string;
  documentIds: string[];
  chatIds: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Chat {
  id: string;
  name: string;
  projectId?: string; // Optional - für allgemeinen Chat
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: any[];
}

type ViewType = 'general-chat' | 'project' | 'system';

const MainApp: React.FC = () => {
  const [activeView, setActiveView] = useState<ViewType>('general-chat');
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [chats, setChats] = useState<Chat[]>([]);
  const [expandedProjects, setExpandedProjects] = useState<Set<string>>(new Set());
  const [showNewProjectDialog, setShowNewProjectDialog] = useState(false);

  useEffect(() => {
    // Load initial data
    loadProjects();
    loadChats();
  }, []);

  const loadProjects = () => {
    // TODO: API call to load projects
    const mockProjects: Project[] = [
      {
        id: '1',
        name: 'Research Papers',
        description: 'Academic research and papers',
        documentIds: [],
        chatIds: [],
        createdAt: new Date(),
        updatedAt: new Date()
      },
      {
        id: '2', 
        name: 'Company Docs',
        description: 'Internal company documentation',
        documentIds: [],
        chatIds: [],
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ];
    setProjects(mockProjects);
  };

  const loadChats = () => {
    // TODO: API call to load chats
    const mockChats: Chat[] = [
      {
        id: '1',
        name: 'General Discussion',
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ];
    setChats(mockChats);
  };

  const createProject = (name: string, description: string) => {
    const newProject: Project = {
      id: Date.now().toString(),
      name,
      description,
      documentIds: [],
      chatIds: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    setProjects(prev => [...prev, newProject]);
    setShowNewProjectDialog(false);
  };

  const toggleProjectExpansion = (projectId: string) => {
    setExpandedProjects(prev => {
      const newSet = new Set(prev);
      if (newSet.has(projectId)) {
        newSet.delete(projectId);
      } else {
        newSet.add(projectId);
      }
      return newSet;
    });
  };

  const selectProject = (projectId: string) => {
    setSelectedProjectId(projectId);
    setActiveView('project');
  };

  const getProjectChats = (projectId: string) => {
    return chats.filter(chat => chat.projectId === projectId);
  };

  const getGeneralChats = () => {
    return chats.filter(chat => !chat.projectId);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">RagFlow</h1>
              <p className="text-sm text-gray-500">AI Document Assistant</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto p-4">
          {/* General Chat */}
          <div className="mb-6">
            <button
              onClick={() => setActiveView('general-chat')}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                activeView === 'general-chat'
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <MessageSquare className="w-5 h-5" />
              <div>
                <div className="font-medium">General Chat</div>
                <div className="text-xs text-gray-500">
                  {getGeneralChats().length} conversation{getGeneralChats().length !== 1 ? 's' : ''}
                </div>
              </div>
            </button>
          </div>

          {/* Projects */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
                Projects
              </h3>
              <button
                onClick={() => setShowNewProjectDialog(true)}
                className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            
            <div className="space-y-1">
              {projects.map((project) => (
                <div key={project.id}>
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => toggleProjectExpansion(project.id)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                    >
                      {expandedProjects.has(project.id) ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                    </button>
                    
                    <button
                      onClick={() => selectProject(project.id)}
                      className={`flex-1 flex items-center space-x-2 px-2 py-2 rounded-lg text-left transition-colors ${
                        activeView === 'project' && selectedProjectId === project.id
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <FolderOpen className="w-4 h-4" />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium truncate">{project.name}</div>
                        <div className="text-xs text-gray-500">
                          {project.documentIds.length} docs • {getProjectChats(project.id).length} chats
                        </div>
                      </div>
                    </button>
                  </div>

                  {/* Project Chats */}
                  {expandedProjects.has(project.id) && (
                    <div className="ml-6 mt-1 space-y-1">
                      {getProjectChats(project.id).map((chat) => (
                        <button
                          key={chat.id}
                          className="w-full flex items-center space-x-2 px-2 py-1 text-sm text-gray-600 hover:bg-gray-50 rounded"
                        >
                          <MessageSquare className="w-3 h-3" />
                          <span className="truncate">{chat.name}</span>
                        </button>
                      ))}
                      <button className="w-full flex items-center space-x-2 px-2 py-1 text-sm text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded">
                        <Plus className="w-3 h-3" />
                        <span>New Chat</span>
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* System */}
          <div>
            <button
              onClick={() => setActiveView('system')}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                activeView === 'system'
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Activity className="w-5 h-5" />
              <div>
                <div className="font-medium">System Status</div>
                <div className="text-xs text-gray-500">Health & monitoring</div>
              </div>
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            <div>RagFlow v1.0.0</div>
            <div className="mt-1">Powered by AI</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {activeView === 'general-chat' && <GeneralChat />}
        {activeView === 'project' && selectedProjectId && (
          <ProjectView 
            project={projects.find(p => p.id === selectedProjectId)!}
            onProjectUpdate={(updatedProject) => {
              setProjects(prev => prev.map(p => p.id === updatedProject.id ? updatedProject : p));
            }}
          />
        )}
        {activeView === 'system' && <SystemStatus />}
      </div>

      {/* New Project Dialog */}
      {showNewProjectDialog && (
        <NewProjectDialog 
          onCreateProject={createProject}
          onClose={() => setShowNewProjectDialog(false)}
        />
      )}
    </div>
  );
};

// New Project Dialog Component
const NewProjectDialog: React.FC<{
  onCreateProject: (name: string, description: string) => void;
  onClose: () => void;
}> = ({ onCreateProject, onClose }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onCreateProject(name.trim(), description.trim());
      setName('');
      setDescription('');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Create New Project</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project name..."
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description (optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe your project..."
              rows={3}
            />
          </div>
          
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 text-white bg-blue-500 rounded-md hover:bg-blue-600 transition-colors"
            >
              Create Project
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MainApp;