using FundLens.Compliance.Domain;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace FundLens.Compliance.Pages;

public sealed class IndexModel(ReportStore store) : PageModel
{
    public IReadOnlyList<ComplianceReport> Reports { get; private set; } = [];

    public void OnGet() => Reports = store.Latest();
}
