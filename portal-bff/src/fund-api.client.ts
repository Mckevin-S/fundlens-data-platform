import { HttpException, HttpStatus, Injectable } from "@nestjs/common";

export interface NavDto { fundId: string; asOf: string; netAssets: number; navPerShare: number }
export interface PerformanceDto { fundId: string; from: string; to: string; periodReturn: number; contributions: Record<string, number> }
export interface DocumentDto { id: string; type: string; title: string; language: string; publishedOn: string }

export const FUND_API_URL = "FUND_API_URL";
export type FetchFn = typeof fetch;

/** Client HTTP de fund-api : traduit les erreurs en réponses HTTP propres au BFF. */
@Injectable()
export class FundApiClient {
  constructor(private readonly baseUrl: string, private readonly fetchFn: FetchFn = fetch) {}

  nav(fundId: string, asOf: string): Promise<NavDto> {
    return this.call(`/api/funds/${encodeURIComponent(fundId)}/nav/${asOf}`, "POST");
  }

  performance(fundId: string, from: string, to: string): Promise<PerformanceDto> {
    return this.call(`/api/funds/${encodeURIComponent(fundId)}/performance?from=${from}&to=${to}`);
  }

  documents(fundId: string): Promise<DocumentDto[]> {
    return this.call(`/api/funds/${encodeURIComponent(fundId)}/documents`);
  }

  private async call<T>(path: string, method = "GET"): Promise<T> {
    let response: Response;
    try {
      response = await this.fetchFn(`${this.baseUrl}${path}`, { method, headers: { Accept: "application/json" } });
    } catch {
      throw new HttpException("fund-api injoignable", HttpStatus.BAD_GATEWAY);
    }
    if (!response.ok) {
      const status = response.status === 404 || response.status === 400 ? response.status : HttpStatus.BAD_GATEWAY;
      throw new HttpException(`fund-api a répondu ${response.status}`, status);
    }
    return (await response.json()) as T;
  }
}
