using Microsoft.AspNetCore.Mvc;
using ControlPlane.Models;
using ControlPlane.Services;

namespace ControlPlane.Controllers;

[ApiController]
[Route("api/[controller]")]
public class CefController : ControllerBase
{
    private readonly ILedgerService _ledgerService;
    private readonly IMemoryStore _memoryStore;

    public CefController(ILedgerService ledgerService, IMemoryStore memoryStore)
    {
        _ledgerService = ledgerService;
        _memoryStore = memoryStore;
    }

    [HttpGet("claims")]
    public async Task<ActionResult<List<ClaimRecord>>> GetClaims([FromQuery] string? service)
    {
        var claims = await _ledgerService.GetClaimsAsync();
        if (!string.IsNullOrEmpty(service))
            claims = claims.Where(c => c.Service.Equals(service, StringComparison.OrdinalIgnoreCase)).ToList();
        return Ok(claims);
    }

    [HttpGet("contradictions")]
    public async Task<ActionResult<List<ContradictionRecord>>> GetContradictions()
    {
        return Ok(await _ledgerService.GetContradictionsAsync());
    }

    [HttpGet("ledger")]
    public async Task<ActionResult<List<LedgerEntry>>> GetLedger()
    {
        return Ok(await _ledgerService.GetLedgerEntriesAsync());
    }

    [HttpGet("latest-analysis")]
    public ActionResult<RCABundle> GetLatestAnalysis()
    {
        if (_memoryStore.LatestAnalysis == null) return NotFound();
        return Ok(_memoryStore.LatestAnalysis);
    }
}
