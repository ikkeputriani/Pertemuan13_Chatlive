import { DatePipe } from '@angular/common';
import { Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ChatService } from './chat.service';

@Component({
  selector: 'app-root',
  imports: [DatePipe, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private readonly chat = inject(ChatService);
  protected readonly status = toSignal(this.chat.status$, { initialValue: 'disconnected' });
  protected readonly messages = toSignal(this.chat.messages$, { initialValue: [] });
  protected readonly errorMessage = toSignal(this.chat.errorMessage$, { initialValue: null });
  protected readonly connectionLabel = computed(() => {
    switch (this.status()) {
      case 'connected':
        return 'Terhubung';
      case 'connecting':
        return 'Menghubungkan...';
      case 'reconnecting':
        return 'Menyambungkan kembali...';
      default:
        return 'Tidak terhubung';
    }
  });

  protected displayName = '';
  protected draft = '';

  constructor() {
    void this.connect();
  }

  protected async retryConnection(): Promise<void> {
    await this.connect();
  }

  protected async sendMessage(): Promise<void> {
    const user = this.displayName.trim();
    const content = this.draft.trim();
    if (!user || !content || this.status() !== 'connected') {
      return;
    }

    try {
      await this.chat.sendMessage(user, content);
      this.draft = '';
    } catch {
      // The service exposes the failure through errorMessage$ for the chat UI.
    }
  }

  protected initials(user: string): string {
    return user
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join('');
  }

  private async connect(): Promise<void> {
    try {
      await this.chat.connect();
    } catch {
      // The service exposes the connection failure through errorMessage$.
    }
  }
}
