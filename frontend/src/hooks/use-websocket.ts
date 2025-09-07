// hooks/useProgressWebSocket.ts
import { useState, useEffect, useCallback, useRef } from "react";

export interface ProgressMessage {
  type: "progress";
  message: string;
  step: string;
  current: number;
  total: number;
  repo_name: string;
  timestamp: string;
  alert?: {
    type: "success" | "warning" | "error" | "info";
    message: string;
  };
}

export interface ProgressState {
  isConnected: boolean;
  currentMessage: string;
  currentStep: string;
  progress: number;
  currentRepo: string;
  history: ProgressMessage[];
  alerts: Array<{
    id: string;
    type: "success" | "warning" | "error" | "info";
    message: string;
    timestamp: string;
  }>;
}

export const useProgressWebSocket = (url: string) => {
  const [state, setState] = useState<ProgressState>({
    isConnected: false,
    currentMessage: "Waiting to start...",
    currentStep: "idle",
    progress: 0,
    currentRepo: "",
    history: [],
    alerts: [],
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        setState((prev) => ({
          ...prev,
          isConnected: true,
          currentMessage: "Connected to progress stream",
        }));
        console.log("WebSocket connected to:", url);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data: ProgressMessage = JSON.parse(event.data);

          setState((prev) => {
            const newHistory = [...prev.history, data];
            const progress =
              data.total > 0
                ? (data.current / data.total) * 100
                : prev.progress;

            const newAlerts = [...prev.alerts];
            if (data.alert) {
              newAlerts.push({
                id: `${Date.now()}-${Math.random()}`,
                type: data.alert.type,
                message: data.alert.message,
                timestamp: data.timestamp,
              });

              // Keep only last 10 alerts
              if (newAlerts.length > 10) {
                newAlerts.splice(0, newAlerts.length - 10);
              }
            }

            return {
              ...prev,
              currentMessage: data.message,
              currentStep: data.step,
              progress,
              currentRepo: data.repo_name,
              history: newHistory.slice(-50), // Keep last 50 messages
              alerts: newAlerts,
            };
          });
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      wsRef.current.onclose = (event) => {
        setState((prev) => ({
          ...prev,
          isConnected: false,
          currentMessage: "Disconnected from progress stream",
        }));
        console.log("WebSocket disconnected:", event.reason);

        // Attempt to reconnect after 3 seconds if not a clean close
        if (event.code !== 1000 && event.code !== 1001) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log("Attempting to reconnect...");
            connect();
          }, 3000);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error("WebSocket error:", error);
        setState((prev) => ({
          ...prev,
          isConnected: false,
          currentMessage: "Connection error occurred",
        }));
      };
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      setState((prev) => ({
        ...prev,
        isConnected: false,
        currentMessage: "Failed to establish connection",
      }));
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, "User initiated disconnect");
      wsRef.current = null;
    }

    setState((prev) => ({
      ...prev,
      isConnected: false,
      currentMessage: "Disconnected",
    }));
  }, []);

  const clearHistory = useCallback(() => {
    setState((prev) => ({ ...prev, history: [] }));
  }, []);

  const clearAlerts = useCallback(() => {
    setState((prev) => ({ ...prev, alerts: [] }));
  }, []);

  const removeAlert = useCallback((alertId: string) => {
    setState((prev) => ({
      ...prev,
      alerts: prev.alerts.filter((alert) => alert.id !== alertId),
    }));
  }, []);

  const reset = useCallback(() => {
    setState({
      isConnected: false,
      currentMessage: "Waiting to start...",
      currentStep: "idle",
      progress: 0,
      currentRepo: "",
      history: [],
      alerts: [],
    });
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    clearHistory,
    clearAlerts,
    removeAlert,
    reset,
  };
};
