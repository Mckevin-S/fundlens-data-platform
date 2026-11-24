using FundLens.Compliance.Domain;
using Xunit;

namespace FundLens.Compliance.Tests;

public class RatioCheckerTests
{
    private static readonly DateOnly Day = new(2026, 11, 20);
    private readonly RatioChecker _checker = new();

    private static ComplianceRequest Request(decimal cash, params (string Issuer, decimal Value)[] lines) =>
        new("FL-0001", Day, 1_000_000m, cash,
            lines.Select((l, i) => new Holding($"FR00000000{i:D2}", l.Issuer, l.Value)).ToList());

    [Fact]
    public void Portefeuille_diversifie_conforme()
    {
        var report = _checker.Check(Request(50_000m, ("A", 80_000m), ("B", 70_000m), ("C", 40_000m)));

        Assert.True(report.Compliant);
        Assert.Empty(report.Violations);
    }

    [Fact]
    public void Emetteur_au_dela_de_10_pourcents()
    {
        var report = _checker.Check(Request(0m, ("TotalEnergies", 120_000m)));

        Assert.False(report.Compliant);
        var v = Assert.Single(report.Violations, x => x.Rule == "ratio-emetteur");
        Assert.Equal(Severity.Breach, v.Severity);
        Assert.Equal(0.12m, v.Actual);
    }

    [Fact]
    public void Lignes_d_un_meme_emetteur_cumulees()
    {
        var report = _checker.Check(Request(0m, ("BNP", 60_000m), ("BNP", 50_000m)));

        Assert.Contains(report.Violations, v => v.Rule == "ratio-emetteur" && v.Actual == 0.11m);
    }

    [Fact]
    public void Somme_des_emetteurs_au_dela_de_5_pourcents_limitee_a_40()
    {
        var lines = Enumerable.Range(0, 5).Select(i => ($"E{i}", 90_000m)).ToArray();

        var report = _checker.Check(Request(0m, lines));

        var v = Assert.Single(report.Violations, x => x.Rule == "ratio-5-40");
        Assert.Equal(0.45m, v.Actual);
        Assert.False(report.Compliant);
    }

    [Fact]
    public void Alerte_preventive_a_90_pourcents_de_la_limite()
    {
        var report = _checker.Check(Request(0m, ("A", 95_000m)));

        Assert.True(report.Compliant);
        Assert.Equal(Severity.Warning, Assert.Single(report.Violations).Severity);
    }

    [Fact]
    public void Liquidites_excessives()
    {
        var report = _checker.Check(Request(250_000m));

        Assert.Contains(report.Violations, v => v.Rule == "ratio-liquidites" && v.Severity == Severity.Breach);
    }

    [Fact]
    public void Actif_net_nul_refuse()
    {
        Assert.Throws<ArgumentException>(() => _checker.Check(new ComplianceRequest("FL-0001", Day, 0m, 0m, [])));
    }
}
