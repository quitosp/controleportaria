namespace WebApi.Core.Multitenant;

public interface IUnidadeContext
{
    Guid? UnidadeId { get; }
    Guid? PortariaPadraoId { get; }
    string? Papel { get; }
    bool EstaAutenticado { get; }
    Guid UnidadeIdObrigatoria();
}
