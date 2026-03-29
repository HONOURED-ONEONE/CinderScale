using System.Text.Json.Serialization;

namespace ControlPlane.Models;

public class Manifest
{
    [JsonPropertyName("run_id")]
    public string RunId { get; set; } = string.Empty;
}

public class RunData
{
    [JsonPropertyName("manifest")]
    public Manifest Manifest { get; set; } = new Manifest();

    [JsonPropertyName("alerts")]
    public List<object> Alerts { get; set; } = new List<object>();

    [JsonPropertyName("logs")]
    public List<object> Logs { get; set; } = new List<object>();

    [JsonPropertyName("metrics")]
    public List<object> Metrics { get; set; } = new List<object>();

    [JsonPropertyName("traces")]
    public List<object> Traces { get; set; } = new List<object>();

    [JsonPropertyName("changes")]
    public List<object> Changes { get; set; } = new List<object>();
}

public class Hypothesis
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }
}

public class PipelineResult
{
    [JsonPropertyName("run_id")]
    public string RunId { get; set; } = string.Empty;

    [JsonPropertyName("tss")]
    public double Tss { get; set; }

    [JsonPropertyName("top3")]
    public List<Hypothesis> Top3 { get; set; } = new();
    
    [JsonPropertyName("epistemic_state")]
    public EpistemicState? EpistemicState { get; set; }
}

public class EpistemicState
{
    [JsonPropertyName("health_claims")]
    public List<HealthClaim> HealthClaims { get; set; } = new();

    [JsonPropertyName("contradictions")]
    public List<Contradiction> Contradictions { get; set; } = new();
}

public class HealthClaim
{
    [JsonPropertyName("service")]
    public string Service { get; set; } = string.Empty;

    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;

    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }
}

public class Contradiction
{
    [JsonPropertyName("service")]
    public string Service { get; set; } = string.Empty;

    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;

    [JsonPropertyName("severity")]
    public string Severity { get; set; } = string.Empty;
}

public class RCABundle
{
    [JsonPropertyName("kept")]
    public string Kept { get; set; } = string.Empty;
    
    [JsonPropertyName("baseline")]
    public PipelineResult? Baseline { get; set; }
    
    [JsonPropertyName("final")]
    public PipelineResult? Final { get; set; }

    [JsonPropertyName("forecasting")]
    public object? Forecasting { get; set; }

    [JsonPropertyName("probes")]
    public List<object> Probes { get; set; } = new();
}
