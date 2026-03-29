using System;
using System.Collections.Generic;

namespace ControlPlane.Models;

public class ClaimRecord
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string RunId { get; set; } = string.Empty;
    public string Service { get; set; } = string.Empty;
    public string State { get; set; } = string.Empty;
    public double Confidence { get; set; }
    public string Rationale { get; set; } = string.Empty;
}

public class ContradictionRecord
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string RunId { get; set; } = string.Empty;
    public string Service { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Severity { get; set; } = string.Empty;
}

public class LedgerEntry
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string RunId { get; set; } = string.Empty;
    public string EventType { get; set; } = string.Empty; // e.g., "AnalysisComplete", "ProbeTriggered"
    public string Details { get; set; } = string.Empty;
}
