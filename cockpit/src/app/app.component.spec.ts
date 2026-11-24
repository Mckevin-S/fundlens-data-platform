import { ComponentFixture, TestBed } from '@angular/core/testing';
import { registerLocaleData } from '@angular/common';
import localeFr from '@angular/common/locales/fr';
import { LOCALE_ID } from '@angular/core';
import { of, throwError } from 'rxjs';
import { AppComponent } from './app.component';
import { FundService } from './fund.service';

registerLocaleData(localeFr);

describe('AppComponent', () => {
  let fixture: ComponentFixture<AppComponent>;
  let funds: jasmine.SpyObj<FundService>;

  beforeEach(async () => {
    funds = jasmine.createSpyObj<FundService>('FundService', ['computeNav', 'performance', 'alerts', 'contributions']);
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [{ provide: FundService, useValue: funds }, { provide: LOCALE_ID, useValue: 'fr' }],
    }).compileComponents();
    fixture = TestBed.createComponent(AppComponent);
  });

  const text = (selector: string) =>
    (fixture.nativeElement as HTMLElement).querySelector(selector)?.textContent?.replace(/\s+/g, ' ').trim();

  it('affiche VL, performance, contributions et alertes', () => {
    funds.computeNav.and.returnValue(of({ fundId: 'FL-0001', asOf: '2026-11-23', netAssets: 1737900.75, navPerShare: 13.9032 }));
    funds.performance.and.returnValue(of({ fundId: 'FL-0001', from: '2026-11-20', to: '2026-11-23', periodReturn: 0.004015, contributions: { X: 0.01 } }));
    funds.alerts.and.returnValue(of([{ asOf: '2026-11-24', variation: -0.07, message: 'Variation de VL de -6.84 %' }]));
    funds.contributions.and.returnValue([{ isin: 'FR0000120271', value: 0.010954 }, { isin: 'FR0000131104', value: -0.00825 }]);

    fixture.componentInstance.refresh();
    fixture.detectChanges();

    expect(text('[data-testid=nav]')).toBe('13,9032 €');
    expect(text('[data-testid=perf]')).toBe('0,40 %');
    expect(text('[data-testid=alert]')).toContain('-6.84 %');
    expect(fixture.componentInstance.barWidth(-0.00825)).toBe(75);
    expect(funds.computeNav).toHaveBeenCalledWith('FL-0001', '2026-11-23');
  });

  it('affiche le détail d\'erreur renvoyé par fund-api', () => {
    funds.computeNav.and.returnValue(throwError(() => ({ status: 404, error: { detail: 'Aucun inventaire' } })));
    funds.performance.and.returnValue(of());
    funds.alerts.and.returnValue(of([]));

    fixture.componentInstance.refresh();
    fixture.detectChanges();

    expect(text('[role=alert]')).toBe('Aucun inventaire');
    expect(fixture.componentInstance.loading()).toBeFalse();
  });
});
