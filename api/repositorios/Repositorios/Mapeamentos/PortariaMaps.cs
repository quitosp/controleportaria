using Dominios.Portarias.Entidades;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Repositorios.Mapeamentos;

public class PortariaMaps : IEntityTypeConfiguration<Portaria>
{
    public void Configure(EntityTypeBuilder<Portaria> builder)
    {
        builder.HasKey(l => l.Id);
        builder.Property(l => l.Id).ValueGeneratedOnAdd().HasColumnName("PortariaId");
        builder.Property(l => l.Nome).IsRequired(true).HasColumnType("varchar(200)");
        builder.Property(l => l.UnidadeId).IsRequired(true);
    }
}
