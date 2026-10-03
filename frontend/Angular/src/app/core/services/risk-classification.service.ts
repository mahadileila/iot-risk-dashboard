import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { RiskClassificationBand } from '../models/risk-classification.model';

@Injectable({ providedIn: 'root' })
export class RiskClassificationService {
  constructor(private api: ApiService) {}

  getClassifications() {
    return this.api.get<RiskClassificationBand[]>('/risk-classifications');
  }
}