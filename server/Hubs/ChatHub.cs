using ChatLive.Server.Models;
using Microsoft.AspNetCore.SignalR;

namespace ChatLive.Server.Hubs;

public sealed class ChatHub : Hub
{
    private const int MaxUserLength = 30;
    private const int MaxMessageLength = 500;

    public async Task SendMessage(string? user, string? content)
    {
        var displayName = user?.Trim();
        var text = content?.Trim();

        if (string.IsNullOrWhiteSpace(displayName) || displayName.Length > MaxUserLength)
        {
            throw new HubException($"Nama harus terdiri dari 1–{MaxUserLength} karakter.");
        }

        if (string.IsNullOrWhiteSpace(text) || text.Length > MaxMessageLength)
        {
            throw new HubException($"Pesan harus terdiri dari 1–{MaxMessageLength} karakter.");
        }

        var message = new ChatMessage(
            Guid.NewGuid().ToString("N"),
            displayName,
            text,
            DateTimeOffset.UtcNow);

        await Clients.All.SendAsync("ReceiveMessage", message);
    }
}
