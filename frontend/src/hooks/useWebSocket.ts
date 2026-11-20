'use client';
import { useEffect, useRef, useState, useCallback } from 'react';
import wsService from '@/services/websocket';

export function useWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<unknown>(null);
  const urlRef = useRef(url);

  useEffect(() => {
    wsService.connect(urlRef.current);
    const unsub = wsService.subscribe('ping', (data) => {
      setIsConnected(!!(data as { connected?: boolean })?.connected);
    });
    return unsub;
  }, []);

  const subscribe = useCallback(
    (
      event: Parameters<typeof wsService.subscribe>[0],
      handler: Parameters<typeof wsService.subscribe>[1]
    ) => {
      return wsService.subscribe(event, (data) => {
        setLastMessage(data);
        handler(data);
      });
    },
    []
  );

  return {
    isConnected,
    lastMessage,
    subscribe,
    send: wsService.send.bind(wsService),
  };
}
