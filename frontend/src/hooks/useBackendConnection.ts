import { useState, useCallback } from 'react';
import { api } from '@/lib/api';

export function useBackendConnection() {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  const checkConnection = useCallback(async () => {
    setLoading(true);
    
    try {
      await api.healthCheck();
      setIsConnected(true);
    } catch (error) {
      setIsConnected(false);
      console.error('Backend connection failed:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    isConnected,
    loading,
    checkConnection
  };
}
