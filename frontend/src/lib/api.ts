// File: frontend/src/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  provider?: string;
  max_tokens?: number;
  temperature?: number;
  max_results?: number;
  conversation_history?: ConversationMessage[];
}

export interface ConversationMessage {
  role: string;
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  message: string;
  sources: SearchResult[];
  provider: string;
  tokens_used: number;
  success: boolean;
  error?: string;
  metadata?: any;
}

export interface SearchResult {
  id: string;
  document_id: string;
  document_filename: string;
  text: string;
  score: number;
  chunk_index: number;
}

export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  content_type: string;
  file_size: number;
  status: string;
  created_at: string;
  processing_completed_at?: string;
  chunks_count?: number;
}

export interface ProvidersResponse {
  providers: string[];
  default_provider?: string;
}

export interface HealthResponse {
  rag_service: string;
  providers: Record<string, string>;
  vector_service: string;
  search_service: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  // Health and System
  async ping(): Promise<{ message: string }> {
    return this.request('/ping');
  }

  async getProviders(): Promise<ProvidersResponse> {
    return this.request('/api/v1/chat/providers');
  }

  async getChatHealth(): Promise<HealthResponse> {
    return this.request('/api/v1/chat/health');
  }

  // Chat
  async chat(request: ChatRequest): Promise<ChatResponse> {
    return this.request('/api/v1/chat/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async simpleChat(request: Omit<ChatRequest, 'max_results'>): Promise<ChatResponse> {
    return this.request('/api/v1/chat/simple', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Documents
  async uploadDocument(file: File, collectionId?: string): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    if (collectionId) {
      formData.append('collection_id', collectionId);
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Upload failed: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async getDocuments(skip: number = 0, limit: number = 100): Promise<{ documents: Document[]; total: number }> {
  return this.request(`/api/v1/documents/?skip=${skip}&limit=${limit}`);
  }

  async getDocument(documentId: string): Promise<Document> {
    return this.request(`/api/v1/documents/${documentId}`);
  }

  async deleteDocument(documentId: string): Promise<void> {
    await this.request(`/api/v1/documents/${documentId}`, {
      method: 'DELETE',
    });
  }

  // Search
  async semanticSearch(query: string, limit: number = 5): Promise<{ results: SearchResult[] }> {
    return this.request('/api/v1/search/semantic', {
      method: 'POST',
      body: JSON.stringify({ query, limit }),
    });
  }

  // Test endpoints
  async testProvider(provider: string, message: string = 'Test message'): Promise<any> {
    return this.request(`/api/v1/chat/test?provider=${provider}&message=${encodeURIComponent(message)}`, {
      method: 'POST',
    });
  }

  async getStats(): Promise<any> {
    return this.request('/api/v1/chat/stats');
  }
}

// Create and export the service instance
export const apiService = new ApiService();

// Also export as default for flexibility
export default apiService;