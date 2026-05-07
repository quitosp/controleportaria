namespace Core.Usuarios.Entidade
{
    public class UsuarioRespostaLogin
    {
        public string AccessToken { get; set; }
        public Guid RefreshToken { get; set; }
        public DateTime ExpiresIn { get; set; }
        public UsuarioToken UsuarioToken { get; set; }
    }
}
