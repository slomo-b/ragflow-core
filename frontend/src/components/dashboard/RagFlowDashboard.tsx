'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';
import { UploadTab } from '@/components/tabs/UploadTab';
import { SearchTab } from '@/components/tabs/SearchTab';
import { AdminTab } from '@/components/tabs/AdminTab';
import { ErrorBanner } from '@/components/ui/ErrorBanner';
import { useDocuments } from '@/hooks/useDocuments';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import { useBackendConnection } from '@/hooks/useBackendConnection';

export type TabType = 'upload' | 'search' | 'admin';

export function RagFlowDashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('upload');
  const [error, setError] = useState<string | null>(null);
  
  const { documents, loading: documentsLoading, refreshDocuments } = useDocuments();
  const { systemStatus, refreshSystemStatus } = useSystemStatus();
  const { isConnected: backendConnected, checkConnection } = useBackendConnection();

  useEffect(() => {
    checkConnection();
    refreshDocuments();
    refreshSystemStatus();
  }, []);

  const handleRefresh = () => {
    checkConnection();
    refreshSystemStatus();
    refreshDocuments();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        backendConnected={backendConnected}
        onRefresh={handleRefresh}
      />
      
      {error && (
        <ErrorBanner error={error} onClose={() => setError(null)} />
      )}

      <div className="flex h-[calc(100vh-80px)]">
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          documents={documents}
        />

        <div className="flex-1 flex flex-col">
          {activeTab === 'upload' && (
            <UploadTab
              documents={documents}
              loading={documentsLoading}
              systemStatus={systemStatus}
              backendConnected={backendConnected}
              onDocumentsChange={refreshDocuments}
              onError={setError}
            />
          )}
          
          {activeTab === 'search' && (
            <SearchTab
              documents={documents}
              backendConnected={backendConnected}
              onError={setError}
            />
          )}
          
          {activeTab === 'admin' && (
            <AdminTab
              documents={documents}
              systemStatus={systemStatus}
              backendConnected={backendConnected}
            />
          )}
        </div>
      </div>
    </div>
  );
}