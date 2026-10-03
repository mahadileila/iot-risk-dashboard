import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { RiskFactor, FactorGroup } from '../models/risk-factor.model';

@Injectable({ providedIn: 'root' })
export class RiskFactorService {
  constructor(private api: ApiService) {}

  getRiskFactors() {
    return this.api.get<RiskFactor[]>('/risk-factors');
  }

  getFactorGroups() {
    return this.api.get<FactorGroup[]>('/factor-groups');
  }

  createRiskFactor(factor: { name: string; id_factor_group: string }) {
    return this.api.post<RiskFactor>('/risk-factors', factor);
  }

  updateRiskFactor(id: string, factor: { name: string; id_factor_group: string }) {
    return this.api.put<RiskFactor>(`/risk-factors/${id}`, factor);
  }

  deleteRiskFactor(id: string) {
    return this.api.delete<void>(`/risk-factors/${id}`);
  }
}