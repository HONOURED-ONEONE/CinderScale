using ControlPlane.Models;

namespace ControlPlane.Services;

public interface IMemoryStore
{
    RunData? LatestRunData { get; set; }
    RCABundle? LatestAnalysis { get; set; }
    string ControlPlaneStatus { get; set; }
}

public class MemoryStore : IMemoryStore
{
    public RunData? LatestRunData { get; set; }
    public RCABundle? LatestAnalysis { get; set; }
    public string ControlPlaneStatus { get; set; } = "Initializing";
}
