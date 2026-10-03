import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RiskFactorService } from '../../../core/services/risk-factor.service';
import { RiskFactor } from '../../../core/models/risk-factor.model';

@Component({
  selector: 'app-risk-factor-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './risk-factor-list.html'
})
export class RiskFactorList implements OnInit {
  riskFactors: RiskFactor[] = [];
  loading = true;
  error: string | null = null;

  constructor(
    private riskFactorService: RiskFactorService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.riskFactorService.getRiskFactors().subscribe({
      next: (factors) => {
        this.riskFactors = factors;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = "Unable to load risk factors.";
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  get impactFactors(): RiskFactor[] {
    return this.riskFactors.filter(f => f.group_name === 'impact');
  }

  get likelihoodFactors(): RiskFactor[] {
    return this.riskFactors.filter(f => f.group_name === 'likelihood');
  }
}