import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Notification, NotificationType } from '../../../shared/components/notification/notification';
import { SubsystemService } from '../../../core/services/subsystem.service';
import { BmsSubsystem } from '../../../core/models/subsystem.model';

@Component({
  selector: 'app-bms-subsystem-list',
  standalone: true,
  imports: [CommonModule, FormsModule, Notification],
  templateUrl: './bms-subsystem-list.html'
})
export class BmsSubsystemList implements OnInit {
  subsystems: BmsSubsystem[] = [];
  searchTerm = '';
  loading = true;

  notificationType: NotificationType = null;
  notificationMessage: string | null = null;

  showForm = false;
  editingId: string | null = null;
  formName = '';

  showDeleteForm = false;
  subsystemToDelete: BmsSubsystem | null = null;

  constructor(
    private subsystemService: SubsystemService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadSubsystems();
  }

  get filteredSubsystems(): BmsSubsystem[] {
    if (!this.searchTerm.trim()) return this.subsystems;
    const term = this.searchTerm.toLowerCase();
    return this.subsystems.filter(s => s.name.toLowerCase().includes(term));
  }

  private showNotification(type: NotificationType, message: string) {
    this.notificationType = type;
    this.notificationMessage = message;
    this.cdr.detectChanges();

    setTimeout(() => {
      this.notificationType = null;
      this.notificationMessage = null;
      this.cdr.detectChanges();
    }, 4000);
  }

  loadSubsystems() {
    this.loading = true;
    this.subsystemService.getSubsystems().subscribe({
      next: (data) => {
        this.subsystems = data;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.loading = false;
        this.showNotification('error', "Unable to load subsystems.");
      }
    });
  }

  openAddForm() {
    this.editingId = null;
    this.formName = '';
    this.showForm = true;
  }

  openEditForm(subsystem: BmsSubsystem) {
    this.editingId = subsystem.id_subsystem;
    this.formName = subsystem.name;
    this.showForm = true;
  }

  cancelForm() {
    this.showForm = false;
  }

  saveSubsystem() {
    if (!this.formName.trim()) {
      this.showForm = false;
      this.showNotification('error', "Name is required.");
      return;
    }

    const payload = { name: this.formName };

    const request = this.editingId
      ? this.subsystemService.updateSubsystem(this.editingId, payload)
      : this.subsystemService.createSubsystem(payload);

    request.subscribe({
      next: () => {
        this.showForm = false;
        this.loadSubsystems();
        this.showNotification('success', this.editingId ? "Subsystem updated." : "Subsystem created.");
      },
      error: () => {
        this.showForm = false;
        this.showNotification('error', "Error while saving.");
      }
    });
  }

  deleteSubsystem(subsystem: BmsSubsystem) {
    this.subsystemToDelete = subsystem;
    this.showDeleteForm = true;
  }

  cancelDelete() {
    this.showDeleteForm = false;
    this.subsystemToDelete = null;
  }

  confirmDelete() {
    if (!this.subsystemToDelete) return;

    const target = this.subsystemToDelete;

    this.subsystemService.deleteSubsystem(target.id_subsystem).subscribe({
      next: () => {
        this.showDeleteForm = false;
        this.subsystemToDelete = null;
        this.loadSubsystems();
        this.showNotification('success', `"${target.name}" deleted.`);
      },
      error: (err) => {
        this.showDeleteForm = false;
        this.subsystemToDelete = null;
        this.showNotification(
          'error',
          err.status === 409
            ? "Cannot delete: device types are still linked to this subsystem."
            : "Error while deleting."
        );
        this.cdr.detectChanges();
      }
    });
  }
}