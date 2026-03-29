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
    
    [JsonPropertyName("actions")]
    public List<string>? Actions { get; set; }
}

public class TopologySummary
{
    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }

    [JsonPropertyName("edge_count")]
    public int EdgeCount { get; set; }

    [JsonPropertyName("avg_edge_conf")]
    public double AvgEdgeConf { get; set; }

    [JsonPropertyName("nodes")]
    public Dictionary<string, object>? Nodes { get; set; }

    [JsonPropertyName("edges")]
    public List<object>? Edges { get; set; }
}

public class MEPP
{
    [JsonPropertyName("hypothesis")]
    public string Hypothesis { get; set; } = string.Empty;

    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }

    [JsonPropertyName("minimal_evidence")]
    public List<object> MinimalEvidence { get; set; } = new();

    [JsonPropertyName("recommended_action")]
    public string? RecommendedAction { get; set; }
}

public class PipelineResult
{
    [JsonPropertyName("run_id")]
    public string RunId { get; set; } = string.Empty;

    [JsonPropertyName("incident_id")]
    public string IncidentId { get; set; } = string.Empty;

    [JsonPropertyName("mode")]
    public string Mode { get; set; } = string.Empty;

    [JsonPropertyName("tss")]
    public double Tss { get; set; }

    [JsonPropertyName("top3")]
    public List<Hypothesis> Top3 { get; set; } = new();

    [JsonPropertyName("missing")]
    public List<string> Missing { get; set; } = new();

    [JsonPropertyName("topology_summary")]
    public TopologySummary? TopologySummary { get; set; }

    [JsonPropertyName("mepp")]
    public List<MEPP> Mepp { get; set; } = new();

    [JsonPropertyName("epistemic_state")]
    public EpistemicState? EpistemicState { get; set; }
}

public class EpistemicState
{
    [JsonPropertyName("health_claims")]
    public List<HealthClaim> HealthClaims { get; set; } = new();

    [JsonPropertyName("contradictions")]
    public List<Contradiction> Contradictions { get; set; } = new();

    [JsonPropertyName("reliability_graph_nodes")]
    public List<string> ReliabilityGraphNodes { get; set; } = new();
}

public class HealthClaim
{
    [JsonPropertyName("service")]
    public string Service { get; set; } = string.Empty;

    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;

    [JsonPropertyName("evidence")]
    public string? Evidence { get; set; }

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

    [JsonPropertyName("resolved")]
    public bool Resolved { get; set; }
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

    [JsonPropertyName("action")]
    public string? Action { get; set; }

    [JsonPropertyName("deltas")]
    public Dictionary<string, object>? Deltas { get; set; }
}
