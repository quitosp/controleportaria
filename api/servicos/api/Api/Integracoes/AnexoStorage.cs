using Dominios.MovimentosPortaria.Servicos;
using Microsoft.Extensions.Configuration;

namespace Api.Integracoes;

public class AnexoStorage : IAnexoStorage
{
    private readonly string _basePath;

    public AnexoStorage(IConfiguration configuration)
    {
        _basePath = configuration["Anexos:CaminhoBase"] ?? Path.Combine(AppContext.BaseDirectory, "anexos");
    }

    public async Task<string> Salvar(Guid unidadeId, Guid movimentoId, string nomeOriginal, byte[] conteudo)
    {
        var dir = Path.Combine(_basePath, unidadeId.ToString(), movimentoId.ToString());
        Directory.CreateDirectory(dir);
        var ext = Path.GetExtension(nomeOriginal);
        var nome = $"{Guid.NewGuid()}{ext}";
        var caminho = Path.Combine(dir, nome);
        await File.WriteAllBytesAsync(caminho, conteudo);
        return $"/anexos/{unidadeId}/{movimentoId}/{nome}";
    }
}
