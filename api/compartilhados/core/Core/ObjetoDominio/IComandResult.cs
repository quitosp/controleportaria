namespace Core.ObjetoDominio
{
    public interface IComandResult
    {
        bool Success { get; set; }
        string? Message { get; set; }
        object? Data { get; set; }
        int? Code { get; set; }
    }
}
