import { useState, useCallback } from 'react';
import { Document } from '@/types/document';
import { api } from '@/lib/api';

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.getDocuments();
      setDocuments(response.documents || []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load documents';
      setError(errorMessage);
      console.error('Failed to load documents:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteDocument = useCallback(async (documentId: string) => {
    try {
      await api.deleteDocument(documentId);
      await refreshDocuments();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete document';
      setError(errorMessage);
      throw err;
    }
  }, [refreshDocuments]);

  const uploadDocument = useCallback(async (file: File, collectionId?: string) => {
    try {
      const result = await api.uploadDocument(file, collectionId);
      await refreshDocuments();
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload document';
      setError(errorMessage);
      throw err;
    }
  }, [refreshDocuments]);

  return {
    documents,
    loading,
    error,
    refreshDocuments,
    deleteDocument,
    uploadDocument
  };
}
