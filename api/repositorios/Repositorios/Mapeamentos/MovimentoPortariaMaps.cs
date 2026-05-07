using Dominios.MovimentosPortaria.Entidades;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Repositorios.Mapeamentos;

public class MovimentoPortariaMaps : IEntityTypeConfiguration<MovimentoPortaria>
{
    public void Configure(EntityTypeBuilder<MovimentoPortaria> builder)
    {
        builder.HasKey(l => l.Id);
        builder.Property(l => l.Id).ValueGeneratedOnAdd().HasColumnName("MovimentoPortariaId");

        builder.Property(l => l.UnidadeId).IsRequired(true);
        builder.Property(l => l.PortariaChegadaId).IsRequired(true);
        builder.Property(l => l.PorteiroChegadaId).IsRequired(true).HasColumnType("varchar(450)");
        builder.Property(l => l.DataChegada).IsRequired(true);
        builder.Property(l => l.MotoristaId).IsRequired(true);
        builder.Property(l => l.CarretaId).IsRequired(true);
        builder.Property(l => l.CavaloId);
        builder.Property(l => l.CarretaSegundaId);
        builder.Property(l => l.TransportadoraId);
        builder.Property(l => l.Motivo).IsRequired(true);
        builder.Property(l => l.TipoCarga).IsRequired(true);
        builder.Property(l => l.Destino).IsRequired(true);
        builder.Property(l => l.AutorizadoPorChegada).HasColumnType("varchar(200)");

        builder.Property(l => l.NumeroNFChegada).HasColumnType("varchar(50)");
        builder.Property(l => l.Produto).HasColumnType("varchar(200)");
        builder.Property(l => l.Setor).HasColumnType("varchar(100)");
        builder.Property(l => l.ContratoChegada).HasColumnType("varchar(100)");
        builder.Property(l => l.NumeroContainerChegada).HasColumnType("varchar(50)");
        builder.Property(l => l.Observacao).HasColumnType("varchar(2000)");

        builder.Property(l => l.Estado).IsRequired(true);

        builder.Property(l => l.LiderQueAutorizouId).HasColumnType("varchar(450)");
        builder.Property(l => l.DataChamada);
        builder.Property(l => l.PorteiroEntradaId).HasColumnType("varchar(450)");
        builder.Property(l => l.DataEntrada);
        builder.Property(l => l.PorteiroSaidaId).HasColumnType("varchar(450)");
        builder.Property(l => l.DataSaida);

        builder.Property(l => l.NumeroNFSaida).HasColumnType("varchar(50)");
        builder.Property(l => l.Lacre).HasColumnType("varchar(100)");
        builder.Property(l => l.DestinoSaida).HasColumnType("varchar(200)");
        builder.Property(l => l.NumeroContainerSaida).HasColumnType("varchar(50)");
        builder.Property(l => l.ContratoSaida).HasColumnType("varchar(100)");

        // RN-013 lock otimista
        builder.Property(l => l.RowVersion).IsRowVersion();

        // RN-014 indice multi-tenant + estado para painel
        builder.HasIndex(l => new { l.UnidadeId, l.Estado, l.DataChegada });
        builder.HasIndex(l => new { l.UnidadeId, l.CarretaId, l.Estado });

        // Auditoria/Anexos/Notificacoes — colecoes com cascata
        builder.HasMany(l => l.Eventos)
            .WithOne()
            .HasForeignKey(e => e.MovimentoPortariaId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(l => l.Anexos)
            .WithOne()
            .HasForeignKey(a => a.MovimentoPortariaId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.Ignore(l => l.Notificacoes); // Entity.Notificacoes (Events) — nao mapear

        builder.HasMany(l => l.NotificacoesPendentes)
            .WithOne()
            .HasForeignKey(n => n.MovimentoPortariaId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}

public class EventoFluxoMaps : IEntityTypeConfiguration<EventoFluxo>
{
    public void Configure(EntityTypeBuilder<EventoFluxo> builder)
    {
        builder.HasKey(e => e.Id);
        builder.Property(e => e.Id).ValueGeneratedOnAdd();
        builder.Property(e => e.UsuarioId).IsRequired().HasColumnType("varchar(450)");
        builder.Property(e => e.Detalhes).HasColumnType("varchar(2000)");
        builder.Property(e => e.Quando).IsRequired();
        builder.Property(e => e.Tipo).IsRequired();
        builder.HasIndex(e => new { e.MovimentoPortariaId, e.Quando });
    }
}

public class AnexoMaps : IEntityTypeConfiguration<Anexo>
{
    public void Configure(EntityTypeBuilder<Anexo> builder)
    {
        builder.HasKey(a => a.Id);
        builder.Property(a => a.Id).ValueGeneratedOnAdd();
        builder.Property(a => a.Url).IsRequired().HasColumnType("varchar(1000)");
        builder.Property(a => a.ContentType).IsRequired().HasColumnType("varchar(100)");
        builder.Property(a => a.UsuarioUploadId).IsRequired().HasColumnType("varchar(450)");
        builder.HasIndex(a => new { a.MovimentoPortariaId, a.Estagio });
    }
}

public class NotificacaoPendenteMaps : IEntityTypeConfiguration<NotificacaoPendente>
{
    public void Configure(EntityTypeBuilder<NotificacaoPendente> builder)
    {
        builder.HasKey(n => n.Id);
        builder.Property(n => n.Id).ValueGeneratedOnAdd();
        builder.Property(n => n.Destino).IsRequired().HasColumnType("varchar(500)");
        builder.Property(n => n.Payload).IsRequired().HasColumnType("text");
        builder.Property(n => n.UltimoErro).HasColumnType("varchar(2000)");
        builder.HasIndex(n => new { n.Status, n.ProximaTentativa });
    }
}
