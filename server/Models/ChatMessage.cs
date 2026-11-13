namespace ChatLive.Server.Models;

public sealed record ChatMessage(
    string Id,
    string User,
    string Content,
    DateTimeOffset SentAt);
