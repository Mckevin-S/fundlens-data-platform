import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { Contribution, Nav, NavAlert, Performance } from './fund.models';

/** Accès à fund-api (proxy /api vers localhost:8080 en développement). */
@Injectable({ providedIn: 'root' })
export class FundService {
  private readonly http = inject(HttpClient);

  computeNav(fundId: string, asOf: string): Observable<Nav> {
    return this.http.post<Nav>(`/api/funds/${fundId}/nav/${asOf}`, null);
  }

  performance(fundId: string, from: string, to: string): Observable<Performance> {
    return this.http.get<Performance>(`/api/funds/${fundId}/performance`, { params: { from, to } });
  }

  alerts(fundId: string): Observable<NavAlert[]> {
    return this.http.get<NavAlert[]>(`/api/funds/${fundId}/alerts`);
  }

  /** Contributions triées par valeur absolue décroissante. */
  contributions(perf: Performance): Contribution[] {
    return Object.entries(perf.contributions)
      .map(([isin, value]) => ({ isin, value }))
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  }
}

export const toPercent = map((x: number) => x * 100);
