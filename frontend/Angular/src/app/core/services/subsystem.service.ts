import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { BmsSubsystem } from '../models/subsystem.model';

@Injectable({ providedIn: 'root' })
export class SubsystemService {
  constructor(private api: ApiService) {}

  getSubsystems() {
    return this.api.get<BmsSubsystem[]>('/subsystems');
  }

  createSubsystem(subsystem: Partial<BmsSubsystem>) {
    return this.api.post<BmsSubsystem>('/subsystems', subsystem);
  }

  updateSubsystem(id: string, subsystem: Partial<BmsSubsystem>) {
    return this.api.put<BmsSubsystem>(`/subsystems/${id}`, subsystem);
  }

  deleteSubsystem(id: string) {
    return this.api.delete<void>(`/subsystems/${id}`);
  }
}