export interface Document {
  id: string;
  filename: string;
  content_type: string;
  file_size: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  collection_id?: string;
}

export interface SearchResult {
  id: string;
  score: number;
  document_id: string;
  text: string;
  chunk_index: number;
  timestamp?: string;
}

export interface SystemStatus {
  status: string;
  version: string;
  mode: string;
  services: Record<string, string>;
  configuration: {
    max_file_size_mb: number;
    chunk_size: number;
    embedding_model?: string;
  };
}