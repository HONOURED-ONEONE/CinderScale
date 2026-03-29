using System.Text.Json;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace ControlPlane;

public class OrchestratorWorker : BackgroundService
{
    private readonly ILogger<OrchestratorWorker> _logger;
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly string _sharedCurrentDir = Path.Combine(Directory.GetCurrentDirectory(), "..", "shared_demo_root", "current");

    public OrchestratorWorker(ILogger<OrchestratorWorker> logger, IHttpClientFactory httpClientFactory)
    {
        _logger = logger;
        _httpClientFactory = httpClientFactory;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Control Plane Orchestrator started. Monitoring directory: {dir}", _sharedCurrentDir);
        string lastRunId = string.Empty;

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var manifestPath = Path.Combine(_sharedCurrentDir, "manifest.json");
                var readyPath = Path.Combine(_sharedCurrentDir, "READY");

                if (File.Exists(manifestPath) && File.Exists(readyPath))
                {
                    var runData = await LoadRunDataAsync(_sharedCurrentDir, stoppingToken);
                    var currentRunId = runData.Manifest?.RunId;

                    if (!string.IsNullOrEmpty(currentRunId) && currentRunId != lastRunId)
                    {
                        _logger.LogInformation("New run detected: {RunId}. Forwarding to Python Analytical Engine...", currentRunId);
                        
                        var client = _httpClientFactory.CreateClient("PythonEngine");
                        
                        var requestBody = new { run_data = runData, model_path = "policy/model.joblib" };
                        var response = await client.PostAsJsonAsync("api/v1/analyze", requestBody, stoppingToken);

                        if (response.IsSuccessStatusCode)
                        {
                            var result = await response.Content.ReadAsStringAsync(stoppingToken);
                            _logger.LogInformation("Received Epistemic State & RCA Bundle from Python Engine.");
                            // TODO: Update Persistent Reliability Graph and Handle Probe Orchestration
                        }
                        else
                        {
                            _logger.LogError("Python Engine returned status: {Status}", response.StatusCode);
                        }

                        lastRunId = currentRunId;
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error occurred during Orchestrator loop.");
            }

            await Task.Delay(2000, stoppingToken);
        }
    }

    private async Task<RunData> LoadRunDataAsync(string directory, CancellationToken cancellationToken)
    {
        // Simplistic mock loader reproducing rca.loader.load_run behavior
        // In a production environment, this would cleanly serialize the JSONL files.
        return new RunData { Manifest = new Manifest { RunId = Guid.NewGuid().ToString() } };
    }
}
