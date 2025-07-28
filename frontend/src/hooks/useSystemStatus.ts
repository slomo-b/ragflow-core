import { useState, useCallback } from 'react';
import { SystemStatus } from '@/types/document';
import { api } from '@/lib/api';

export function useSystemStatus() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshSystemStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const status = await api.getSystemStatus();
      setSystemStatus(status);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load system status';
      setError(errorMessage);
      console.error('Failed to load system status:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    systemStatus,
    loading,
    error,
    refreshSystemStatus
  };
}
