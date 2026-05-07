using Dominios.Transportadoras.Entidades;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Repositorios.Mapeamentos;

public class TransportadoraMaps : IEntityTypeConfiguration<Transportadora>
{
    public void Configure(EntityTypeBuilder<Transportadora> builder)
    {
        builder.HasKey(l => l.Id);
        builder.Property(l => l.Id).ValueGeneratedOnAdd().HasColumnName("TransportadoraId");
        builder.Property(l => l.Nome).IsRequired(true).HasColumnType("varchar(200)");
        builder.Property(l => l.RazaoSocial).IsRequired(true).HasColumnType("varchar(200)");
        builder.Property(l => l.Cnpj).IsRequired(true).HasColumnType("varchar(14)");
        builder.Property(l => l.UnidadeId).IsRequired(true);
    }
}
