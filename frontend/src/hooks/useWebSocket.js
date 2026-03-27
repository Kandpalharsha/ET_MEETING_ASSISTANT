import { useEffect, useRef, useCallback } from "react";

const WS_URL = "ws://localhost:8000/ws/audit";

export function useWebSocket(onMessage) {
  const wsRef = useRef(null);
  const retryRef = useRef(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      clearTimeout(retryRef.current);
      onMessage({ type: "connected" });
    };

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type !== "ping") onMessage(msg);
      } catch {}
    };

    ws.onclose = () => {
      onMessage({ type: "disconnected" });
      if (mountedRef.current) {
        retryRef.current = setTimeout(connect, 2000);
      }
    };

    ws.onerror = () => ws.close();
  }, [onMessage]);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      clearTimeout(retryRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return wsRef;
}
