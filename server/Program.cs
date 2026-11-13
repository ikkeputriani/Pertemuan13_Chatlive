using ChatLive.Server.Hubs;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins("http://localhost:4200")
            .AllowAnyHeader()
            .AllowAnyMethod()
            .AllowCredentials();
    });
});
builder.Services.AddSignalR();

var app = builder.Build();

app.UseCors();
app.MapGet("/health", () => Results.Ok(new { status = "ok" }));
app.MapHub<ChatHub>("/chat");

app.Run();
