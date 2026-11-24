import { BadRequestException, Controller, Get, Param, Query } from "@nestjs/common";
import { FundSummary, PortalService } from "./portal.service";

const DATE = /^\d{4}-\d{2}-\d{2}$/;
const FUND = /^FL-\d{4}$/;

@Controller("portal/funds")
export class PortalController {
  constructor(private readonly portal: PortalService) {}

  @Get(":fundId/summary")
  summary(@Param("fundId") fundId: string, @Query("from") from: string, @Query("to") to: string): Promise<FundSummary> {
    if (!FUND.test(fundId)) throw new BadRequestException("Identifiant de fonds invalide");
    if (!DATE.test(from ?? "") || !DATE.test(to ?? "") || from >= to) {
      throw new BadRequestException("Paramètres from et to attendus au format AAAA-MM-JJ, from < to");
    }
    return this.portal.summary(fundId, from, to);
  }
}
