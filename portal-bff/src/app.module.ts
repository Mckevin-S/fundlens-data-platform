import { Module } from "@nestjs/common";
import { FUND_API_URL, FundApiClient } from "./fund-api.client";
import { HealthController } from "./health.controller";
import { PortalController } from "./portal.controller";
import { PortalService } from "./portal.service";

@Module({
  controllers: [PortalController, HealthController],
  providers: [
    { provide: FUND_API_URL, useValue: process.env.FUND_API_URL ?? "http://localhost:8080" },
    { provide: FundApiClient, useFactory: (url: string) => new FundApiClient(url), inject: [FUND_API_URL] },
    PortalService,
  ],
})
export class AppModule {}
