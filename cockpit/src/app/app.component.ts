import { DecimalPipe, PercentPipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { Contribution, Nav, NavAlert, Performance } from './fund.models';
import { FundService } from './fund.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, DecimalPipe, PercentPipe],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  private readonly funds = inject(FundService);

  fundId = 'FL-0001';
  from = '2026-11-20';
  to = '2026-11-23';

  readonly nav = signal<Nav | null>(null);
  readonly performance = signal<Performance | null>(null);
  readonly contributions = signal<Contribution[]>([]);
  readonly alerts = signal<NavAlert[]>([]);
  readonly error = signal<string | null>(null);
  readonly loading = signal(false);

  refresh(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      nav: this.funds.computeNav(this.fundId, this.to),
      performance: this.funds.performance(this.fundId, this.from, this.to),
      alerts: this.funds.alerts(this.fundId),
    }).subscribe({
      next: ({ nav, performance, alerts }) => {
        this.nav.set(nav);
        this.performance.set(performance);
        this.contributions.set(this.funds.contributions(performance));
        this.alerts.set(alerts);
        this.loading.set(false);
      },
      error: (e: { status?: number; error?: { detail?: string } }) => {
        this.error.set(e.error?.detail ?? `fund-api indisponible (${e.status ?? 'réseau'})`);
        this.loading.set(false);
      },
    });
  }

  /** Largeur de barre (0–100 %) relative à la plus forte contribution. */
  barWidth(value: number): number {
    const max = Math.max(...this.contributions().map((c) => Math.abs(c.value)), 1e-9);
    return Math.round((Math.abs(value) / max) * 100);
  }
}
