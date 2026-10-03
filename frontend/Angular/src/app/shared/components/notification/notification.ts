import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type NotificationType = 'error' | 'success' | null;

@Component({
  selector: 'app-notification',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notification.html'
})
export class Notification {
  @Input() type: NotificationType = null;
  @Input() message: string | null = null;
}