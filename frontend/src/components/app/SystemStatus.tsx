// File: frontend/src/components/app/SystemStatus.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  RefreshCw,
  Server,
  Database,
  Bot,
  Search,
  Zap
} from 'lucide-react';
import { apiService } from '@/lib/api';

const SystemStatus: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    fetchSystemStatus();
    const interval = setInterval(fetchSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      setLoading(true);
      const [healthData, statsData] = await Promise.all([
        apiService.getChatHealth(),
        apiService.getStats().catch(() => null)
      ]);
      
      setHealth(healthData);
      setStats(statsData);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'available':
      case 'connected':
        return 'text-green-500';
      case 'unhealthy':
      case 'error':
      case 'unavailable':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'available':
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'unhealthy':
      case 'error':
      case 'unavailable':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-600 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-800">System Status</h1>
              <p className="text-sm text-gray-500">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </p>
            </div>
          </div>
          
          <button
            onClick={fetchSystemStatus}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Overall Status */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Server className="w-8 h-8 text-blue-500" />
              <div>
                <h2 className="text-lg font-semibold text-gray-800">RagFlow System</h2>
                <p className="text-sm text-gray-600">AI Document Assistant</p>
              </div>
            </div>
            
            <div className="text-right">
              {health ? (
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-6 h-6 text-green-500" />
                  <span className="text-lg font-medium text-green-600">Online</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <XCircle className="w-6 h-6 text-red-500" />
                  <span className="text-lg font-medium text-red-600">Offline</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Core Services */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <Bot className="w-8 h-8 text-purple-500" />
              {getStatusIcon(health?.rag_service || 'unknown')}
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">RAG Service</h3>
            <p className="text-sm text-gray-600 mb-3">Main AI processing service</p>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">Status:</span>
              <span className={`text-sm font-medium capitalize ${getStatusColor(health?.rag_service || 'unknown')}`}>
                {health?.rag_service || 'Unknown'}
              </span>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <Search className="w-8 h-8 text-blue-500" />
              {getStatusIcon(health?.vector_service || 'unknown')}
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Vector Database</h3>
            <p className="text-sm text-gray-600 mb-3">Qdrant vector storage</p>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">Status:</span>
              <span className={`text-sm font-medium capitalize ${getStatusColor(health?.vector_service || 'unknown')}`}>
                {health?.vector_service || 'Unknown'}
              </span>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <Database className="w-8 h-8 text-green-500" />
              {getStatusIcon(health?.search_service || 'unknown')}
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Search Service</h3>
            <p className="text-sm text-gray-600 mb-3">Document retrieval</p>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">Status:</span>
              <span className={`text-sm font-medium capitalize ${getStatusColor(health?.search_service || 'unknown')}`}>
                {health?.search_service || 'Unknown'}
              </span>
            </div>
          </div>
        </div>

        {/* LLM Providers */}
        {health?.providers && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">LLM Providers</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(health.providers).map(([provider, status]) => (
                <div key={provider} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Zap className="w-5 h-5 text-purple-500" />
                    <span className="font-medium text-gray-800 capitalize">{provider}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(status as string)}
                    <span className={`text-sm font-medium capitalize ${getStatusColor(status as string)}`}>
                      {status as string}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* System Statistics */}
        {stats && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">System Statistics</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 mb-1">
                  {stats.llm_providers?.count || 0}
                </div>
                <div className="text-sm text-gray-600">LLM Providers</div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">
                  {stats.documents?.total_count || 0}
                </div>
                <div className="text-sm text-gray-600">Documents</div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 mb-1">
                  {stats.vector_service?.collections_count || 0}
                </div>
                <div className="text-sm text-gray-600">Collections</div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600 mb-1">
                  {stats.rag_config?.max_context_chunks || 0}
                </div>
                <div className="text-sm text-gray-600">Max Context</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemStatus;