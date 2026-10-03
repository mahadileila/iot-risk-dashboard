import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RiskClassificationService } from '../../../core/services/risk-classification.service';
import { RiskClassificationBand } from '../../../core/models/risk-classification.model';

@Component({
  selector: 'app-risk-classification-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './risk-classification-list.html'
})
export class RiskClassificationList implements OnInit {
  classifications: RiskClassificationBand[] = [];
  loading = true;
  error: string | null = null;

  constructor(
    private riskClassificationService: RiskClassificationService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.riskClassificationService.getClassifications().subscribe({
      next: (data) => {
        this.classifications = data;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = "Unable to load risk classifications.";
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }
}