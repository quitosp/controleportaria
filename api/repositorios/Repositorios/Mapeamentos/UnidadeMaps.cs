using Dominios.Unidades.Entidades;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Repositorios.Mapeamentos;

public class UnidadeMaps : IEntityTypeConfiguration<Unidade>
{
    public void Configure(EntityTypeBuilder<Unidade> builder)
    {
        builder.HasKey(l => l.Id);
        builder.Property(l => l.Id).ValueGeneratedOnAdd().HasColumnName("UnidadeId");
        builder.Property(l => l.Nome).IsRequired(true).HasColumnType("varchar(200)");
        builder.Property(l => l.ConfiguracaoEvolutionApiUrl).HasColumnType("varchar(500)");
        builder.Property(l => l.ConfiguracaoEvolutionApiToken).HasColumnType("varchar(500)");
    }
}
