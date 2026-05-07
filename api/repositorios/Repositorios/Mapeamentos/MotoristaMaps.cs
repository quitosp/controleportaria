using Dominios.Motoristas.Entidades;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Repositorios.Mapeamentos;

public class MotoristaMaps : IEntityTypeConfiguration<Motorista>
{
    public void Configure(EntityTypeBuilder<Motorista> builder)
    {
        builder.HasKey(l => l.Id);
        builder.Property(l => l.Id).ValueGeneratedOnAdd().HasColumnName("MotoristaId");
        builder.Property(l => l.Nome).IsRequired(true).HasColumnType("varchar(200)");
        builder.Property(l => l.Cpf).IsRequired(true).HasColumnType("varchar(11)");
        builder.Property(l => l.Whatsapp).IsRequired(true).HasColumnType("varchar(20)");
        builder.Property(l => l.Email).HasColumnType("varchar(200)");
        builder.Property(l => l.Status).IsRequired(true);
        builder.Property(l => l.MotivoStatus).HasColumnType("varchar(500)");
        builder.Property(l => l.UnidadeId).IsRequired(true);
    }
}
