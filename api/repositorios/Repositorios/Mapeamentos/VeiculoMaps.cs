using Dominios.Veiculos.Entidades;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Repositorios.Mapeamentos;

public class VeiculoMaps : IEntityTypeConfiguration<Veiculo>
{
    public void Configure(EntityTypeBuilder<Veiculo> builder)
    {
        builder.HasKey(l => l.Id);
        builder.Property(l => l.Id).ValueGeneratedOnAdd().HasColumnName("VeiculoId");
        builder.Property(l => l.Nome).IsRequired(true).HasColumnType("varchar(200)");
        builder.Property(l => l.Placa).IsRequired(true).HasColumnType("varchar(8)");
        builder.Property(l => l.Tipo).IsRequired(true);
        builder.Property(l => l.TransportadoraId);
        builder.Property(l => l.UnidadeId).IsRequired(true);
    }
}
