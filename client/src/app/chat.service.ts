import { Injectable } from '@angular/core';
import {
  HubConnection,
  HubConnectionBuilder,
  HubConnectionState,
  LogLevel,
} from '@microsoft/signalr';
import { BehaviorSubject } from 'rxjs';
import { ChatMessage } from './chat-message';

export type ChatConnectionState =
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'disconnected';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly connection: HubConnection;
  private readonly statusSubject = new BehaviorSubject<ChatConnectionState>('disconnected');
  private readonly messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  private readonly errorMessageSubject = new BehaviorSubject<string | null>(null);
  private connectionAttempt: Promise<void> | null = null;

  readonly status$ = this.statusSubject.asObservable();
  readonly messages$ = this.messagesSubject.asObservable();
  readonly errorMessage$ = this.errorMessageSubject.asObservable();

  constructor() {
    this.connection = new HubConnectionBuilder()
      .withUrl('/chat')
      .withAutomaticReconnect()
      .configureLogging(LogLevel.Warning)
      .build();

    this.connection.on('ReceiveMessage', (message: ChatMessage) => {
      this.messagesSubject.next([...this.messagesSubject.value, message].slice(-200));
    });
    this.connection.onreconnecting(() => this.statusSubject.next('reconnecting'));
    this.connection.onreconnected(() => this.statusSubject.next('connected'));
    this.connection.onclose((error) => {
      this.statusSubject.next('disconnected');
      if (error) {
        this.errorMessageSubject.next('Koneksi terputus. Periksa server, lalu coba lagi.');
      }
    });
  }

  connect(): Promise<void> {
    if (this.connection.state === HubConnectionState.Connected) {
      return Promise.resolve();
    }
    if (this.connectionAttempt) {
      return this.connectionAttempt;
    }
    if (this.connection.state !== HubConnectionState.Disconnected) {
      return Promise.resolve();
    }

    this.statusSubject.next('connecting');
    this.errorMessageSubject.next(null);
    this.connectionAttempt = this.startConnection();
    return this.connectionAttempt;
  }

  async sendMessage(user: string, content: string): Promise<void> {
    this.errorMessageSubject.next(null);
    try {
      await this.connection.invoke('SendMessage', user, content);
    } catch (error) {
      this.errorMessageSubject.next('Pesan gagal dikirim. Periksa koneksi, lalu coba lagi.');
      throw error;
    }
  }

  private async startConnection(): Promise<void> {
    try {
      await this.connection.start();
      this.statusSubject.next('connected');
    } catch (error) {
      this.statusSubject.next('disconnected');
      this.errorMessageSubject.next(
        'Tidak dapat terhubung ke server. Pastikan server ASP.NET Core sedang berjalan.',
      );
      throw error;
    } finally {
      this.connectionAttempt = null;
    }
  }
}
