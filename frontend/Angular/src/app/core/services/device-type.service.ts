import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { DeviceType } from '../models/device-type.model';

@Injectable({ providedIn: 'root' })
export class DeviceTypeService {
  constructor(private api: ApiService) {}

  getDeviceTypes() {
    return this.api.get<DeviceType[]>('/device-types');
  }

  createDeviceType(deviceType: Partial<DeviceType>) {
    return this.api.post<DeviceType>('/device-types', deviceType);
  }

  updateDeviceType(id: string, deviceType: Partial<DeviceType>) {
    return this.api.put<DeviceType>(`/device-types/${id}`, deviceType);
  }

  deleteDeviceType(id: string) {
    return this.api.delete<void>(`/device-types/${id}`);
  }
}