import type { ServerMessage } from "@/types/protocol";

interface VerifierSocketHandlers {
  onMessage: (message: ServerMessage) => void;
  onClose: () => void;
}

/** Envoltorio fino sobre WebSocket: solo transporte, sin lógica de UI. */
export class VerifierSocket {
  private socket: WebSocket;

  constructor(url: string, handlers: VerifierSocketHandlers) {
    this.socket = new WebSocket(url);
    this.socket.onmessage = (event) => {
      handlers.onMessage(JSON.parse(event.data) as ServerMessage);
    };
    this.socket.onclose = handlers.onClose;
  }

  sendFrame(base64Jpeg: string): void {
    if (this.socket.readyState !== WebSocket.OPEN) return;
    this.socket.send(JSON.stringify({ type: "frame", data: base64Jpeg }));
  }

  close(): void {
    this.socket.close();
  }
}
