using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace ControlPlane;

public class Program
{
    public static void Main(string[] args)
    {
        CreateHostBuilder(args).Build().Run();
    }

    public static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .ConfigureServices((hostContext, services) =>
            {
                services.AddHttpClient("PythonEngine", client =>
                {
                    client.BaseAddress = new Uri("http://localhost:8000/");
                });
                services.AddHostedService<OrchestratorWorker>();
            });
}
