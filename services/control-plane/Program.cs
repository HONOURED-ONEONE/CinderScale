using ControlPlane.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure the HttpClient for calling Python API
var pythonApiUrl = builder.Configuration.GetValue<string>("ControlPlane:PythonAnalyticsBaseUrl") ?? "http://localhost:8000/";
builder.Services.AddHttpClient<IPythonAnalyticsClient, PythonAnalyticsClient>(client =>
{
    client.BaseAddress = new Uri(pythonApiUrl);
});

// Singleton in-memory store to decouple polling background job from REST API responses
builder.Services.AddSingleton<IMemoryStore, MemoryStore>();

// Register LedgerService for persistence
builder.Services.AddSingleton<ILedgerService, LedgerService>();

// Register background poller
builder.Services.AddHostedService<RunFolderPoller>();

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();
app.UseAuthorization();
app.MapControllers();

app.Run();
