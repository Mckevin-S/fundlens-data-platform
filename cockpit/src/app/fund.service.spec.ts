import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { FundService } from './fund.service';

describe('FundService', () => {
  let service: FundService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(FundService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('calcule la VL par POST', () => {
    service.computeNav('FL-0001', '2026-11-20').subscribe((nav) => expect(nav.navPerShare).toBe(13.8476));
    const req = http.expectOne('/api/funds/FL-0001/nav/2026-11-20');
    expect(req.request.method).toBe('POST');
    req.flush({ fundId: 'FL-0001', asOf: '2026-11-20', netAssets: 1730943.75, navPerShare: 13.8476 });
  });

  it('demande la performance avec les dates en paramètres', () => {
    service.performance('FL-0001', '2026-11-20', '2026-11-23').subscribe();
    const req = http.expectOne((r) => r.url === '/api/funds/FL-0001/performance');
    expect(req.request.params.get('from')).toBe('2026-11-20');
    expect(req.request.params.get('to')).toBe('2026-11-23');
    req.flush({});
  });

  it('trie les contributions par valeur absolue', () => {
    const sorted = service.contributions({
      fundId: 'FL-0001', from: 'a', to: 'b', periodReturn: 0,
      contributions: { A: 0.001, B: -0.008, C: 0.01 },
    });
    expect(sorted.map((c) => c.isin)).toEqual(['C', 'B', 'A']);
  });
});
