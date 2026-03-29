using Microsoft.AspNetCore.Mvc;

namespace ControlPlane.Controllers;

[ApiController]
[Route("[controller]")]
public class HealthController : ControllerBase
{
    [HttpGet]
    public IActionResult Get()
    {
        return Ok(new { Status = "Healthy", Service = "ControlPlane.NET" });
    }
}
