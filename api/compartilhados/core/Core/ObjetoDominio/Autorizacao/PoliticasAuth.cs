namespace Core.ObjetoDominio.Autorizacao;

public static class PoliticasAuth
{
    public const string PorteiroOuMaior = "PorteiroOuMaior";
    public const string LiderOuMaior = "LiderOuMaior";
    public const string SupervisorOuMaior = "SupervisorOuMaior";
    public const string SomenteAdmin = "SomenteAdmin";

    public const string ClaimPapel = "papel";
    public const string ClaimUnidadeId = "unidadeId";
    public const string ClaimPortariaPadraoId = "portariaPadraoId";
}
