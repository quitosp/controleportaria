using Core.ObjetoDominio.Autorizacao;
using Microsoft.AspNetCore.Identity;

namespace WebApi.Core.Usuario
{
    public class Usuario : IdentityUser
    {
        public string Nome { get; set; }
        public string SobreNome { get; set; }
        public bool Status { get; set; } = true;

        public PapelUsuario Papel { get; set; } = PapelUsuario.Porteiro;
        public Guid? UnidadeId { get; set; }
        public Guid? PortariaPadraoId { get; set; }

        public void SetarStatus(bool status)
        {
            Status = status;
        }

        public void DefinirPapel(PapelUsuario papel) => Papel = papel;
        public void DefinirUnidade(Guid? unidadeId, Guid? portariaPadraoId)
        {
            UnidadeId = unidadeId;
            PortariaPadraoId = portariaPadraoId;
        }
    }
}
