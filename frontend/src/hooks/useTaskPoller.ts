import { useState, useEffect, useRef } from 'react';
import { fetchTaskStatus } from '@/lib/api';
import type { TaskStatus, PredictionResult } from '@/types';

interface UseTaskPollerOptions {
  taskId: string | null;
  onComplete: (result: PredictionResult) => void;
  onError: (error: string) => void;
  interval?: number;
}

export function useTaskPoller({ taskId, onComplete, onError, interval = 1500 }: UseTaskPollerOptions) {
  const [isPolling, setIsPolling] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!taskId) {
      setIsPolling(false);
      return;
    }

    setIsPolling(true);

    const poll = async () => {
      try {
        const status: TaskStatus = await fetchTaskStatus(taskId);

        if (status.status === 'completed' && status.result) {
          setIsPolling(false);
          if (timerRef.current) clearInterval(timerRef.current);
          onComplete({
            risk_score: status.result.risk_score,
            risk_level: status.result.risk_level,
            version: status.result.version,
            framework: status.result.framework,
          });
        } else if (status.status === 'failed') {
          setIsPolling(false);
          if (timerRef.current) clearInterval(timerRef.current);
          onError(status.error ?? 'Задача завершилась с ошибкой');
        }
      } catch (e) {
        setIsPolling(false);
        if (timerRef.current) clearInterval(timerRef.current);
        onError('Ошибка опроса статуса задачи');
      }
    };

    // Poll immediately, then on interval
    poll();
    timerRef.current = setInterval(poll, interval);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [taskId]);

  return { isPolling };
}
