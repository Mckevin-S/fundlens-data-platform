using System.Collections.Concurrent;

namespace FundLens.Compliance.Domain;

/// <summary>Derniers contrôles effectués (mémoire du service, affichés dans le back-office).</summary>
public sealed class ReportStore
{
    private readonly ConcurrentQueue<ComplianceReport> _reports = new();
    private const int Capacity = 200;

    public void Add(ComplianceReport report)
    {
        _reports.Enqueue(report);
        while (_reports.Count > Capacity && _reports.TryDequeue(out _))
        {
        }
    }

    public IReadOnlyList<ComplianceReport> Latest() => _reports.Reverse().ToList();
}
