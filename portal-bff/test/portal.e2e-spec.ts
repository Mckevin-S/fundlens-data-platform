import { INestApplication } from "@nestjs/common";
import { Test } from "@nestjs/testing";
import request from "supertest";
import { AppModule } from "../src/app.module";
import { PortalService } from "../src/portal.service";

describe("BFF (e2e)", () => {
  let app: INestApplication;
  const summary = jest.fn().mockResolvedValue({ fundId: "FL-0001", navPerShare: 13.9032 });

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({ imports: [AppModule] })
      .overrideProvider(PortalService).useValue({ summary })
      .compile();
    app = moduleRef.createNestApplication();
    await app.init();
  });

  afterAll(() => app.close());

  it("GET /portal/funds/:id/summary", async () => {
    const res = await request(app.getHttpServer()).get("/portal/funds/FL-0001/summary?from=2026-11-20&to=2026-11-23").expect(200);
    expect(res.body.navPerShare).toBe(13.9032);
    expect(summary).toHaveBeenCalledWith("FL-0001", "2026-11-20", "2026-11-23");
  });

  it("valide les paramètres", async () => {
    await request(app.getHttpServer()).get("/portal/funds/XX/summary?from=2026-11-20&to=2026-11-23").expect(400);
    await request(app.getHttpServer()).get("/portal/funds/FL-0001/summary?from=2026-11-23&to=2026-11-20").expect(400);
  });

  it("GET /health", () => request(app.getHttpServer()).get("/health").expect(200, { status: "UP" }));
});
