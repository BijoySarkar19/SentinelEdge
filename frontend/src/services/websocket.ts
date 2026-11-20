type EventHandler = (data: unknown) => void;
type EventType =
  | 'incident.new'
  | 'incident.updated'
  | 'camera.status'
  | 'system.metrics'
  | 'ping';

class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string = '';
  private handlers: Map<EventType, Set<EventHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private isConnected = false;
  private pingInterval: ReturnType<typeof setInterval> | null = null;

  connect(url: string): void {
    this.url = url;
    this.createConnection();
  }

  private createConnection(): void {
    if (typeof window === 'undefined') return;
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.startPing();
        this.emit('ping', { connected: true });
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.stopPing();
        this.scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.isConnected = false;
      };

      this.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data as string);
          this.emit(msg.type as EventType, msg.data);
        } catch {
          // Ignore malformed messages
        }
      };
    } catch {
      // Ignore connection errors; reconnect will handle
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
    setTimeout(() => {
      this.reconnectAttempts++;
      this.createConnection();
    }, this.reconnectDelay);
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
  }

  private startPing(): void {
    this.pingInterval = setInterval(() => {
      this.send({ type: 'ping' });
    }, 30000);
  }

  private stopPing(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  subscribe(event: EventType, handler: EventHandler): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);
    return () => this.handlers.get(event)?.delete(handler);
  }

  private emit(event: EventType, data: unknown): void {
    this.handlers.get(event)?.forEach((h) => h(data));
  }

  send(data: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect(): void {
    this.ws?.close();
    this.stopPing();
  }

  get connected(): boolean {
    return this.isConnected;
  }
}

export const wsService = new WebSocketService();
export default wsService;
