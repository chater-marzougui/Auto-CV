import { useEffect, useState } from "react";

export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<any[]>([]);

  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };
    return () => ws.close();
  }, [url]);

  return messages;
}
