import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { CollectionInstance } from '../models/instance.model';

@Injectable({ providedIn: 'root' })
export class InstanceService {
  constructor(private api: ApiService) {}

  createInstance(instance: { id_device: string; data_description: string; is_active: boolean }) {
    return this.api.post<CollectionInstance>('/instances', instance);
  }

  updateInstance(id: string, instance: Partial<CollectionInstance>) {
    return this.api.put<CollectionInstance>(`/instances/${id}`, instance);
  }

  deleteInstance(id: string) {
    return this.api.delete<void>(`/instances/${id}`);
  }

  createFactorScore(score: { rating: number; id_instance: string; id_factor: string }) {
    return this.api.post('/instance-factor-scores', score);
  }
}