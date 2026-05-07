using Core.Exeptions;
using Microsoft.AspNetCore.Http;

namespace WebApi.Core.Multitenant;

public class UnidadeContextHttp : IUnidadeContext
{
    private readonly IHttpContextAccessor _accessor;

    public UnidadeContextHttp(IHttpContextAccessor accessor)
    {
        _accessor = accessor;
    }

    public bool EstaAutenticado => _accessor.HttpContext?.User?.Identity?.IsAuthenticated ?? false;

    public string? Papel => ObterClaim("papel");

    public Guid? UnidadeId
    {
        get
        {
            var v = ObterClaim("unidadeId");
            return Guid.TryParse(v, out var g) ? g : null;
        }
    }

    public Guid? PortariaPadraoId
    {
        get
        {
            var v = ObterClaim("portariaPadraoId");
            return Guid.TryParse(v, out var g) ? g : null;
        }
    }

    public Guid UnidadeIdObrigatoria()
    {
        // RN-014 — multi-tenant: usuario sem unidade nao pode acessar dados da unidade
        return UnidadeId ?? throw new DominioException("Usuario sem unidade vinculada.");
    }

    private string? ObterClaim(string nome)
    {
        return _accessor.HttpContext?.User?.FindFirst(nome)?.Value;
    }
}
