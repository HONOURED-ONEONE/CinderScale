using System.Text.Json.Serialization;

namespace ControlPlane;

// Basic model contracts expected by the Python analytical API
public class RunData
{
    [JsonPropertyName("manifest")]
    public Manifest? Manifest { get; set; }

    [JsonPropertyName("alerts")]
    public List<object> Alerts { get; set; } = new();

    [JsonPropertyName("logs")]
    public List<object> Logs { get; set; } = new();

    [JsonPropertyName("metrics")]
    public List<object> Metrics { get; set; } = new();

    [JsonPropertyName("traces")]
    public List<object> Traces { get; set; } = new();

    [JsonPropertyName("changes")]
    public List<object> Changes { get; set; } = new();
}

public class Manifest
{
    [JsonPropertyName("run_id")]
    public string? RunId { get; set; }
}
