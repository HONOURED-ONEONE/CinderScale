using ControlPlane.Models;
using ControlPlane.Services;
using Microsoft.AspNetCore.Mvc;

namespace ControlPlane.Controllers;

[ApiController]
[Route("control")]
public class ControlController : ControllerBase
{
    private readonly IMemoryStore _memoryStore;
    private readonly IPythonAnalyticsClient _pythonClient;

    public ControlController(IMemoryStore memoryStore, IPythonAnalyticsClient pythonClient)
    {
        _memoryStore = memoryStore;
        _pythonClient = pythonClient;
    }

    [HttpGet("status")]
    public IActionResult GetStatus()
    {
        return Ok(new
        {
            Status = _memoryStore.ControlPlaneStatus,
            LatestRunId = _memoryStore.LatestRunData?.Manifest.RunId,
            HasAnalysis = _memoryStore.LatestAnalysis != null
        });
    }

    [HttpGet("latest-run")]
    public IActionResult GetLatestRun()
    {
        if (_memoryStore.LatestRunData == null) return NotFound("No run data loaded yet.");
        return Ok(_memoryStore.LatestRunData);
    }

    [HttpGet("latest-analysis")]
    public IActionResult GetLatestAnalysis()
    {
        if (_memoryStore.LatestAnalysis == null) return NotFound("No analysis loaded yet.");
        return Ok(_memoryStore.LatestAnalysis);
    }

    [HttpPost("trigger-run-analysis")]
    public async Task<IActionResult> TriggerRunAnalysis([FromBody] RunData runData)
    {
        var result = await _pythonClient.AnalyzeRunAsync(runData);
        if (result == null) return StatusCode(500, "Python analysis failed.");
        
        // Optionally update memory store, or just return result
        return Ok(result);
    }
}
