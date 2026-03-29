using Xunit;
using Moq;
using Microsoft.Extensions.Logging;
using ControlPlane.Services;
using ControlPlane.Models;
using System.IO;

namespace ControlPlane.Tests;

public class LedgerServiceTests
{
    private readonly Mock<ILogger<LedgerService>> _loggerMock = new();

    [Fact]
    public async Task RecordEventAsync_AppendsToFile()
    {
        var storagePath = "ledger_data.json";
        if (File.Exists(storagePath)) File.Delete(storagePath);

        var service = new LedgerService(_loggerMock.Object);

        await service.RecordEventAsync("run-1", "TestEvent", "Details");

        Assert.True(File.Exists(storagePath));
        var content = await File.ReadAllTextAsync(storagePath);
        Assert.Contains("TestEvent", content);

        if (File.Exists(storagePath)) File.Delete(storagePath);
    }
}
