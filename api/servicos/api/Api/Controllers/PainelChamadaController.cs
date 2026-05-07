using Core.ObjetoDominio.Autorizacao;
using Dominios.MovimentosPortaria.Comandos.Saidas;
using Dominios.MovimentosPortaria.IRepositorios;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using WebApi.Core.Controller;
using WebApi.Core.Multitenant;

namespace Api.Controllers;

[Route("api/painel-chamada")]
[Authorize(Policy = PoliticasAuth.LiderOuMaior)]
public class PainelChamadaController : MainController
{
    private readonly IMovimentoPortariaRepositorio _repositorio;
    private readonly IUnidadeContext _unidade;
    private readonly int _ttlMinutos;

    public PainelChamadaController(
        IMovimentoPortariaRepositorio repositorio,
        IUnidadeContext unidade,
        IConfiguration cfg)
    {
        _repositorio = repositorio;
        _unidade = unidade;
        _ttlMinutos = int.TryParse(cfg["Notificacoes:TTLChamadaMinutos"], out var v) ? v : 30;
    }

    [HttpGet("v1/listar")]
    public async Task<List<PainelChamadaItemSaida>> Listar()
        => await _repositorio.ListarPainelChamada(_unidade.UnidadeIdObrigatoria(), _ttlMinutos);
}
