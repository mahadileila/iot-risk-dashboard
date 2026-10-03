import { Component, OnInit, AfterViewInit, ChangeDetectorRef, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Chart, registerables } from 'chart.js';
import { DashboardService } from '../../../core/services/dashboard.service';
import { DashboardSummary, RiskTrendPoint } from '../../../core/models/dashboard.model';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.html'
})
export class Dashboard implements OnInit, AfterViewInit {
  @ViewChild('subsystemChartCanvas') subsystemChartCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('trendCanvas') trendCanvas!: ElementRef<HTMLCanvasElement>;

  summary: DashboardSummary | null = null;
  trend: RiskTrendPoint[] = [];
  loading = true;
  error: string | null = null;

  private subsystemChart: Chart | null = null;
  private trendChart: Chart | null = null;

  constructor(
    private dashboardService: DashboardService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.dashboardService.getSummary().subscribe({
      next: (summary) => {
        this.summary = summary;
        this.dashboardService.getRiskTrend().subscribe({
          next: (trend) => {
            this.trend = trend;
            this.loading = false;
            this.cdr.detectChanges();
            this.renderCharts();
          },
          error: () => {
            this.loading = false;
            this.cdr.detectChanges();
            this.renderCharts();
          }
        });
      },
      error: () => {
        this.error = "Unable to load dashboard data.";
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  ngAfterViewInit() {
    if (this.summary) {
      this.renderCharts();
    }
  }

  private renderCharts() {
    this.renderSubsystemChart();
  }

  private renderSubsystemChart() {
    if (!this.subsystemChartCanvas || !this.summary || this.summary.risk_by_subsystem.length === 0) return;

    if (this.subsystemChart) {
      this.subsystemChart.destroy();
    }

    const data = this.summary.risk_by_subsystem;

    this.subsystemChart = new Chart(this.subsystemChartCanvas.nativeElement, {
      type: 'bar',
      data: {
        labels: data.map(s => s.subsystem_name),
        datasets: [{
          label: 'Average risk score',
          data: data.map(s => s.average_score),
          backgroundColor: data.map(s => s.classification.color),
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: { min: 0, max: 100, title: { display: true, text: 'Average score' } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}