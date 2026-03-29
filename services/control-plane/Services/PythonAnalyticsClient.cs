using System.Net.Http.Json;
using ControlPlane.Models;

namespace ControlPlane.Services;

public interface IPythonAnalyticsClient
{
    Task<RCABundle?> AnalyzeRunAsync(RunData runData, CancellationToken cancellationToken = default);
}

public class PythonAnalyticsClient : IPythonAnalyticsClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<PythonAnalyticsClient> _logger;

    public PythonAnalyticsClient(HttpClient httpClient, ILogger<PythonAnalyticsClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<RCABundle?> AnalyzeRunAsync(RunData runData, CancellationToken cancellationToken = default)
    {
        try
        {
            var response = await _httpClient.PostAsJsonAsync("/analyze/run", runData, cancellationToken);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadFromJsonAsync<RCABundle>(cancellationToken: cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to call Python Analytics Engine.");
            return null;
        }
    }
}
