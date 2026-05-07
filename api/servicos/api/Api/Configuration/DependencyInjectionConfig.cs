using Core.Mediator;
using Core.ObjetoDominio;
using MediatR;
using Repositorios.Contexto;
using WebApi.Core.Multitenant;
using WebApi.Core.Usuario;
using WebAPI.Core.Identidade;
using Dominios.Unidades.Comandos.Entradas;
using Dominios.Unidades.Comandos.Handlers;
using Dominios.Unidades.IRepositorios;
using Repositorios.Repositorio;
using Dominios.Portarias.Comandos.Entradas;
using Dominios.Portarias.Comandos.Handlers;
using Dominios.Portarias.IRepositorios;
using Dominios.Transportadoras.Comandos.Entradas;
using Dominios.Transportadoras.Comandos.Handlers;
using Dominios.Transportadoras.IRepositorios;
using Dominios.Veiculos.Comandos.Entradas;
using Dominios.Veiculos.Comandos.Handlers;
using Dominios.Veiculos.IRepositorios;
using Dominios.Motoristas.Comandos.Entradas;
using Dominios.Motoristas.Comandos.Handlers;
using Dominios.Motoristas.IRepositorios;
using Dominios.MovimentosPortaria.Comandos.Entradas;
using Dominios.MovimentosPortaria.Comandos.Handlers;
using Dominios.MovimentosPortaria.IRepositorios;
using Dominios.MovimentosPortaria.Servicos;
using Api.Integracoes;
using Api.BackgroundServices;

namespace Api.Configuration;

public static class DependencyInjectionConfig
{
    public static void RegisterServices(this IServiceCollection services)
    {
        services.AddScoped<IRequestHandler<CadastrarChegadaEntrada, ComandResult>, MovimentoPortariaCommandHandler>();
        services.AddScoped<IRequestHandler<ChamarVeiculoEntrada, ComandResult>, MovimentoPortariaCommandHandler>();
        services.AddScoped<IRequestHandler<RecancelarChamadaEntrada, ComandResult>, MovimentoPortariaCommandHandler>();
        services.AddScoped<IRequestHandler<ConfirmarEntradaEntrada, ComandResult>, MovimentoPortariaCommandHandler>();
        services.AddScoped<IRequestHandler<RegistrarSaidaEntrada, ComandResult>, MovimentoPortariaCommandHandler>();
        services.AddScoped<IRequestHandler<CancelarMovimentoEntrada, ComandResult>, MovimentoPortariaCommandHandler>();
        services.AddScoped<IRequestHandler<DesistirMovimentoEntrada, ComandResult>, MovimentoPortariaCommandHandler>();
        services.AddScoped<IRequestHandler<AlterarMovimentoEntrada, ComandResult>, MovimentoPortariaCommandHandler>();
        services.AddScoped<IRequestHandler<AnexarArquivoEntrada, ComandResult>, MovimentoPortariaCommandHandler>();
        services.AddScoped<IMovimentoPortariaRepositorio, MovimentoPortariaRepositorio>();
        services.AddScoped<INotificacoesPortariaService, NotificacoesPortariaService>();
        services.AddScoped<IAnexoStorage, AnexoStorage>();
        services.AddHttpClient<IEvolutionApiClient, EvolutionApiClient>();
        services.AddScoped<IEmailSender, SmtpEmailSender>();
        services.AddHostedService<NotificacaoWorker>();
        services.AddHostedService<ChamadaExpiradaWorker>();
        services.AddScoped<IRequestHandler<SalvarMotoristaEntrada, ComandResult>, MotoristaCommandHandler>();
        services.AddScoped<IRequestHandler<AlterarMotoristaEntrada, ComandResult>, MotoristaCommandHandler>();
        services.AddScoped<IMotoristaRepositorio, MotoristaRepositorio>();
        services.AddScoped<IRequestHandler<SalvarVeiculoEntrada, ComandResult>, VeiculoCommandHandler>();
        services.AddScoped<IRequestHandler<AlterarVeiculoEntrada, ComandResult>, VeiculoCommandHandler>();
        services.AddScoped<IVeiculoRepositorio, VeiculoRepositorio>();
        services.AddScoped<IRequestHandler<SalvarTransportadoraEntrada, ComandResult>, TransportadoraCommandHandler>();
        services.AddScoped<IRequestHandler<AlterarTransportadoraEntrada, ComandResult>, TransportadoraCommandHandler>();
        services.AddScoped<ITransportadoraRepositorio, TransportadoraRepositorio>();
        services.AddScoped<IRequestHandler<SalvarPortariaEntrada, ComandResult>, PortariaCommandHandler>();
        services.AddScoped<IRequestHandler<AlterarPortariaEntrada, ComandResult>, PortariaCommandHandler>();
        services.AddScoped<IPortariaRepositorio, PortariaRepositorio>();
        services.AddScoped<IRequestHandler<SalvarUnidadeEntrada, ComandResult>, UnidadeCommandHandler>();
        services.AddScoped<IRequestHandler<AlterarUnidadeEntrada, ComandResult>, UnidadeCommandHandler>();
        services.AddScoped<IUnidadeRepositorio, UnidadeRepositorio>();
        services.Configure<AppTokenSettings>(options => { options.RefreshTokenExpiration = 24; });
        services.AddScoped<Api.Identidade.Servicos.AuthenticationService>();
        services.AddSingleton<IHttpContextAccessor, HttpContextAccessor>();
        services.AddScoped<IAspNetUser, AspNetUser>();
        services.AddScoped<IUnidadeContext, UnidadeContextHttp>();
        services.AddScoped<IMediatorHandler, MediatorHandler>();

        services.AddScoped<ContextoDB>();
    }
}
