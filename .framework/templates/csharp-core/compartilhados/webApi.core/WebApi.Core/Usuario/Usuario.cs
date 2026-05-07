using Microsoft.AspNetCore.Identity;

namespace WebApi.Core.Usuario
{
    public class Usuario : IdentityUser
    {
        public string Nome { get; set; }
        public string SobreNome { get; set; }
        public bool Status { get; set; } = true;

        public void SetarStatus(bool status)
        {
            Status = status;
        }
    }
}
