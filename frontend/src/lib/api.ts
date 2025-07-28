import { Document, SearchResult, SystemStatus } from '@/types/document';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

export const api = {
  uploadDocument: async (file: File, collectionId?: string): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    if (collectionId) {
      formData.append('collection_id', collectionId);
    }
    
    const response = await fetch(`${API_BASE}/api/v1/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new ApiError(`Upload failed: ${response.statusText}`, response.status);
    }
    
    return response.json();
  },

  getDocuments: async (skip = 0, limit = 100): Promise<{ documents: Document[]; total: number }> => {
    const response = await fetch(`${API_BASE}/api/v1/documents/?skip=${skip}&limit=${limit}`);
    
    if (!response.ok) {
      throw new ApiError(`Failed to fetch documents: ${response.statusText}`, response.status);
    }
    
    return response.json();
  },

  deleteDocument: async (documentId: string): Promise<{ message: string }> => {
    const response = await fetch(`${API_BASE}/api/v1/documents/${documentId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new ApiError(`Delete failed: ${response.statusText}`, response.status);
    }
    
    return response.json();
  },

  semanticSearch: async (query: string, topK = 5, documentIds?: string[]): Promise<{ results: SearchResult[] }> => {
    const response = await fetch(`${API_BASE}/api/v1/search/semantic`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        top_k: topK,
        document_ids: documentIds,
      }),
    });
    
    if (!response.ok) {
      throw new ApiError(`Search failed: ${response.statusText}`, response.status);
    }
    
    return response.json();
  },

  getSystemStatus: async (): Promise<SystemStatus> => {
    const response = await fetch(`${API_BASE}/api/v1/system/status`);
    
    if (!response.ok) {
      throw new ApiError(`Failed to get system status: ${response.statusText}`, response.status);
    }
    
    return response.json();
  },

  healthCheck: async (): Promise<{ status: string }> => {
    const response = await fetch(`${API_BASE}/api/v1/health/`);
    
    if (!response.ok) {
      throw new ApiError(`Health check failed: ${response.statusText}`, response.status);
    }
    
    return response.json();
  }
};
