export interface Nav { fundId: string; asOf: string; netAssets: number; navPerShare: number }
export interface Performance { fundId: string; from: string; to: string; periodReturn: number; contributions: Record<string, number> }
export interface NavAlert { asOf: string; variation: number; message: string }
export interface Contribution { isin: string; value: number }
