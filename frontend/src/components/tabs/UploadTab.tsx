import React, { useState } from 'react';
import { Upload, FileText, RefreshCw } from 'lucide-react';
import { Document, SystemStatus } from '@/types/document';
import { FileUploadZone } from '@/components/upload/FileUploadZone';
import { SelectedFilesList } from '@/components/upload/SelectedFilesList';
import { DocumentsList } from '@/components/documents/DocumentsList';
import { useDocuments } from '@/hooks/useDocuments';

interface UploadTabProps {
  documents: Document[];
  loading: boolean;
  systemStatus: SystemStatus | null;
  backendConnected: boolean;
  onDocumentsChange: () => void;
  onError: (error: string) => void;
}

export function UploadTab({ 
  documents, 
  loading, 
  systemStatus, 
  backendConnected, 
  onDocumentsChange,
  onError 
}: UploadTabProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const { uploadDocument, deleteDocument } = useDocuments();

  const handleFileUpload = async (files: File[]) => {
    setUploading(true);
    
    try {
      const uploadPromises = files.map(file => uploadDocument(file));
      await Promise.all(uploadPromises);
      setSelectedFiles([]);
      onDocumentsChange();
    } catch (error) {
      onError(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    try {
      await deleteDocument(documentId);
      onDocumentsChange();
    } catch (error) {
      onError(`Delete failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return (
    <div className="flex-1 p-6">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Documents</h2>
        
        <FileUploadZone
          onFilesSelected={setSelectedFiles}
          maxFileSize={systemStatus?.configuration?.max_file_size_mb || 50}
        />

        {selectedFiles.length > 0 && (
          <SelectedFilesList
            files={selectedFiles}
            onFilesChange={setSelectedFiles}
            onUpload={handleFileUpload}
            uploading={uploading}
            backendConnected={backendConnected}
          />
        )}

        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Uploaded Documents</h3>
            <button
              onClick={onDocumentsChange}
              className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200 flex items-center space-x-1"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
          
          <DocumentsList 
            documents={documents}
            onDelete={handleDeleteDocument}
          />
        </div>
      </div>
    </div>
  );
}
