import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { DashboardSummary, RiskTrendPoint } from '../models/dashboard.model';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  constructor(private api: ApiService) {}

  getSummary() {
    return this.api.get<DashboardSummary>('/dashboard/summary');
  }

  getRiskTrend() {
    return this.api.get<RiskTrendPoint[]>('/dashboard/risk-trend');
  }
}