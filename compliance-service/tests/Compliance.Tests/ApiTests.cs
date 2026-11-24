using System.Net;
using System.Net.Http.Json;
using FundLens.Compliance.Domain;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace FundLens.Compliance.Tests;

public class ApiTests(WebApplicationFactory<Program> factory) : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task Controle_puis_historique_et_page_razor()
    {
        var client = factory.CreateClient();
        var request = new ComplianceRequest("FL-0001", new DateOnly(2026, 11, 20), 1_000_000m, 10_000m,
            [new Holding("FR0000120271", "TotalEnergies", 150_000m)]);

        var response = await client.PostAsJsonAsync("/api/compliance/check", request);
        response.EnsureSuccessStatusCode();
        var report = await response.Content.ReadFromJsonAsync<ComplianceReport>();
        Assert.False(report!.Compliant);

        var reports = await client.GetFromJsonAsync<List<ComplianceReport>>("/api/compliance/reports");
        Assert.NotEmpty(reports!);

        var page = await client.GetStringAsync("/");
        Assert.Contains("Dépassement", page);
    }

    [Fact]
    public async Task Actif_net_invalide_400()
    {
        var client = factory.CreateClient();
        var response = await client.PostAsJsonAsync("/api/compliance/check",
            new ComplianceRequest("FL-0001", new DateOnly(2026, 11, 20), 0m, 0m, []));

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }
}
