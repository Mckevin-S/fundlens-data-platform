using System.Globalization;
using FundLens.Compliance.Domain;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
builder.Services.AddSingleton<RatioChecker>();
builder.Services.AddSingleton<ReportStore>();

var app = builder.Build();
CultureInfo.DefaultThreadCurrentCulture = CultureInfo.GetCultureInfo("fr-FR");

app.UseStaticFiles();
app.MapRazorPages();

app.MapPost("/api/compliance/check", (ComplianceRequest request, RatioChecker checker, ReportStore store) =>
{
    try
    {
        var report = checker.Check(request);
        store.Add(report);
        return Results.Ok(report);
    }
    catch (ArgumentException e)
    {
        return Results.Problem(e.Message, statusCode: StatusCodes.Status400BadRequest, title: "Requête invalide");
    }
});

app.MapGet("/api/compliance/reports", (ReportStore store) => Results.Ok(store.Latest()));
app.MapGet("/health", () => Results.Ok(new { status = "UP" }));

app.Run();

public partial class Program
{
}
