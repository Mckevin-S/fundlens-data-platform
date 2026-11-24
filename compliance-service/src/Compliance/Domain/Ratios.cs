namespace FundLens.Compliance.Domain;

/// <summary>Ligne d'inventaire valorisée en euros, rattachée à son émetteur.</summary>
public sealed record Holding(string Isin, string Issuer, decimal Value);

/// <summary>Demande de contrôle : inventaire valorisé d'un fonds à une date.</summary>
public sealed record ComplianceRequest(string FundId, DateOnly AsOf, decimal NetAssets, decimal Cash,
                                       IReadOnlyList<Holding> Holdings);

public enum Severity { Breach, Warning }

public sealed record Violation(string Rule, Severity Severity, string Message, decimal Actual, decimal Limit);

public sealed record ComplianceReport(string FundId, DateOnly AsOf, bool Compliant, IReadOnlyList<Violation> Violations);

/// <summary>
/// Ratios de dispersion d'un OPCVM (règle « 5/10/40 ») et limite de liquidités :
/// un émetteur ≤ 10 % de l'actif net ; la somme des émetteurs au-delà de 5 % ≤ 40 % ;
/// liquidités ≤ 20 % ; alerte préventive à 90 % d'une limite.
/// </summary>
public sealed class RatioChecker
{
    public const decimal IssuerLimit = 0.10m;
    public const decimal LargeIssuerThreshold = 0.05m;
    public const decimal LargeIssuersLimit = 0.40m;
    public const decimal CashLimit = 0.20m;
    public const decimal WarningLevel = 0.90m;

    public ComplianceReport Check(ComplianceRequest request)
    {
        if (request.NetAssets <= 0)
        {
            throw new ArgumentException("L'actif net doit être strictement positif.", nameof(request));
        }

        var violations = new List<Violation>();
        var byIssuer = request.Holdings
            .GroupBy(h => h.Issuer)
            .Select(g => (Issuer: g.Key, Weight: Math.Round(g.Sum(h => h.Value) / request.NetAssets, 6)))
            .OrderByDescending(x => x.Weight)
            .ToList();

        foreach (var (issuer, weight) in byIssuer)
        {
            Evaluate(violations, "ratio-emetteur", $"Émetteur {issuer}", weight, IssuerLimit);
        }

        var largeIssuers = byIssuer.Where(x => x.Weight > LargeIssuerThreshold).Sum(x => x.Weight);
        Evaluate(violations, "ratio-5-40", "Émetteurs au-delà de 5 %", largeIssuers, LargeIssuersLimit);

        var cashWeight = Math.Round(request.Cash / request.NetAssets, 6);
        Evaluate(violations, "ratio-liquidites", "Liquidités", cashWeight, CashLimit);

        var compliant = violations.All(v => v.Severity != Severity.Breach);
        return new ComplianceReport(request.FundId, request.AsOf, compliant, violations);
    }

    private static void Evaluate(List<Violation> violations, string rule, string label, decimal actual, decimal limit)
    {
        if (actual > limit)
        {
            violations.Add(new Violation(rule, Severity.Breach,
                $"{label} : {actual:P2} de l'actif net, limite {limit:P0}", actual, limit));
        }
        else if (actual >= limit * WarningLevel)
        {
            violations.Add(new Violation(rule, Severity.Warning,
                $"{label} : {actual:P2}, proche de la limite {limit:P0}", actual, limit));
        }
    }
}
