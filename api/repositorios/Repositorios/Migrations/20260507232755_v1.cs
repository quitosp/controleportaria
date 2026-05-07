using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace Repositorios.Migrations
{
    /// <inheritdoc />
    public partial class v1 : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "AspNetRoles",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    Name = table.Column<string>(type: "character varying(256)", maxLength: 256, nullable: true),
                    NormalizedName = table.Column<string>(type: "character varying(256)", maxLength: 256, nullable: true),
                    ConcurrencyStamp = table.Column<string>(type: "text", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AspNetRoles", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "AspNetUsers",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    Nome = table.Column<string>(type: "text", nullable: false),
                    SobreNome = table.Column<string>(type: "text", nullable: false),
                    Status = table.Column<bool>(type: "boolean", nullable: false),
                    Papel = table.Column<int>(type: "integer", nullable: false),
                    UnidadeId = table.Column<Guid>(type: "uuid", nullable: true),
                    PortariaPadraoId = table.Column<Guid>(type: "uuid", nullable: true),
                    UserName = table.Column<string>(type: "character varying(256)", maxLength: 256, nullable: true),
                    NormalizedUserName = table.Column<string>(type: "character varying(256)", maxLength: 256, nullable: true),
                    Email = table.Column<string>(type: "character varying(256)", maxLength: 256, nullable: true),
                    NormalizedEmail = table.Column<string>(type: "character varying(256)", maxLength: 256, nullable: true),
                    EmailConfirmed = table.Column<bool>(type: "boolean", nullable: false),
                    PasswordHash = table.Column<string>(type: "text", nullable: true),
                    SecurityStamp = table.Column<string>(type: "text", nullable: true),
                    ConcurrencyStamp = table.Column<string>(type: "text", nullable: true),
                    PhoneNumber = table.Column<string>(type: "text", nullable: true),
                    PhoneNumberConfirmed = table.Column<bool>(type: "boolean", nullable: false),
                    TwoFactorEnabled = table.Column<bool>(type: "boolean", nullable: false),
                    LockoutEnd = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    LockoutEnabled = table.Column<bool>(type: "boolean", nullable: false),
                    AccessFailedCount = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AspNetUsers", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Motoristas",
                columns: table => new
                {
                    MotoristaId = table.Column<Guid>(type: "uuid", nullable: false),
                    Nome = table.Column<string>(type: "varchar(200)", nullable: false),
                    Cpf = table.Column<string>(type: "varchar(11)", nullable: false),
                    Whatsapp = table.Column<string>(type: "varchar(20)", nullable: false),
                    Email = table.Column<string>(type: "varchar(200)", nullable: true),
                    Status = table.Column<int>(type: "integer", nullable: false),
                    MotivoStatus = table.Column<string>(type: "varchar(500)", nullable: true),
                    UnidadeId = table.Column<Guid>(type: "uuid", nullable: false),
                    DataCadastro = table.Column<DateTime>(type: "timestamp without time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Motoristas", x => x.MotoristaId);
                });

            migrationBuilder.CreateTable(
                name: "MovimentosPortaria",
                columns: table => new
                {
                    MovimentoPortariaId = table.Column<Guid>(type: "uuid", nullable: false),
                    UnidadeId = table.Column<Guid>(type: "uuid", nullable: false),
                    PortariaChegadaId = table.Column<Guid>(type: "uuid", nullable: false),
                    PorteiroChegadaId = table.Column<string>(type: "varchar(450)", nullable: false),
                    DataChegada = table.Column<DateTime>(type: "timestamp without time zone", nullable: false),
                    MotoristaId = table.Column<Guid>(type: "uuid", nullable: false),
                    CarretaId = table.Column<Guid>(type: "uuid", nullable: false),
                    CavaloId = table.Column<Guid>(type: "uuid", nullable: true),
                    CarretaSegundaId = table.Column<Guid>(type: "uuid", nullable: true),
                    TransportadoraId = table.Column<Guid>(type: "uuid", nullable: true),
                    Motivo = table.Column<int>(type: "integer", nullable: false),
                    TipoCarga = table.Column<int>(type: "integer", nullable: false),
                    Destino = table.Column<int>(type: "integer", nullable: false),
                    AutorizadoPorChegada = table.Column<string>(type: "varchar(200)", nullable: true),
                    NumeroNFChegada = table.Column<string>(type: "varchar(50)", nullable: true),
                    Produto = table.Column<string>(type: "varchar(200)", nullable: true),
                    Setor = table.Column<string>(type: "varchar(100)", nullable: true),
                    ContratoChegada = table.Column<string>(type: "varchar(100)", nullable: true),
                    NumeroContainerChegada = table.Column<string>(type: "varchar(50)", nullable: true),
                    Observacao = table.Column<string>(type: "varchar(2000)", nullable: true),
                    Estado = table.Column<int>(type: "integer", nullable: false),
                    LiderQueAutorizouId = table.Column<string>(type: "varchar(450)", nullable: true),
                    DataChamada = table.Column<DateTime>(type: "timestamp without time zone", nullable: true),
                    PorteiroEntradaId = table.Column<string>(type: "varchar(450)", nullable: true),
                    DataEntrada = table.Column<DateTime>(type: "timestamp without time zone", nullable: true),
                    PorteiroSaidaId = table.Column<string>(type: "varchar(450)", nullable: true),
                    DataSaida = table.Column<DateTime>(type: "timestamp without time zone", nullable: true),
                    NumeroNFSaida = table.Column<string>(type: "varchar(50)", nullable: true),
                    Lacre = table.Column<string>(type: "varchar(100)", nullable: true),
                    DestinoSaida = table.Column<string>(type: "varchar(200)", nullable: true),
                    NumeroContainerSaida = table.Column<string>(type: "varchar(50)", nullable: true),
                    ContratoSaida = table.Column<string>(type: "varchar(100)", nullable: true),
                    xmin = table.Column<uint>(type: "xid", rowVersion: true, nullable: false),
                    DataCadastro = table.Column<DateTime>(type: "timestamp without time zone", nullable: false),
                    Status = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MovimentosPortaria", x => x.MovimentoPortariaId);
                });

            migrationBuilder.CreateTable(
                name: "Portarias",
                columns: table => new
                {
                    PortariaId = table.Column<Guid>(type: "uuid", nullable: false),
                    Nome = table.Column<string>(type: "varchar(200)", nullable: false),
                    UnidadeId = table.Column<Guid>(type: "uuid", nullable: false),
                    DataCadastro = table.Column<DateTime>(type: "timestamp without time zone", nullable: false),
                    Status = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Portarias", x => x.PortariaId);
                });

            migrationBuilder.CreateTable(
                name: "RefreshTokens",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Username = table.Column<string>(type: "text", nullable: false),
                    Token = table.Column<Guid>(type: "uuid", nullable: false),
                    ExpirationDate = table.Column<DateTime>(type: "timestamp without time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_RefreshTokens", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "SecurityKeys",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Parameters = table.Column<string>(type: "text", nullable: true),
                    KeyId = table.Column<string>(type: "text", nullable: true),
                    Type = table.Column<string>(type: "text", nullable: true),
                    JwsAlgorithm = table.Column<string>(type: "text", nullable: true),
                    JweAlgorithm = table.Column<string>(type: "text", nullable: true),
                    JweEncryption = table.Column<string>(type: "text", nullable: true),
                    CreationDate = table.Column<DateTime>(type: "timestamp without time zone", nullable: false),
                    JwkType = table.Column<int>(type: "integer", nullable: false),
                    IsRevoked = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_SecurityKeys", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Transportadoras",
                columns: table => new
                {
                    TransportadoraId = table.Column<Guid>(type: "uuid", nullable: false),
                    Nome = table.Column<string>(type: "varchar(200)", nullable: false),
                    RazaoSocial = table.Column<string>(type: "varchar(200)", nullable: false),
                    Cnpj = table.Column<string>(type: "varchar(14)", nullable: false),
                    UnidadeId = table.Column<Guid>(type: "uuid", nullable: false),
                    DataCadastro = table.Column<DateTime>(type: "timestamp without time zone", nullable: false),
                    Status = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Transportadoras", x => x.TransportadoraId);
                });

            migrationBuilder.CreateTable(
                name: "Unidades",
                columns: table => new
                {
                    UnidadeId = table.Column<Guid>(type: "uuid", nullable: false),
                    Nome = table.Column<string>(type: "varchar(200)", nullable: false),
                    ConfiguracaoEvolutionApiUrl = table.Column<string>(type: "varchar(500)", nullable: true),
                    ConfiguracaoEvolutionApiToken = table.Column<string>(type: "varchar(500)", nullable: true),
                    DataCadastro = table.Column<DateTime>(type: "timestamp without time zone", nullable: false),
                    Status = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Unidades", x => x.UnidadeId);
                });

            migrationBuilder.CreateTable(
                name: "Veiculos",
                columns: table => new
                {
                    VeiculoId = table.Column<Guid>(type: "uuid", nullable: false),
                    Nome = table.Column<string>(type: "varchar(200)", nullable: false),
                    Placa = table.Column<string>(type: "varchar(8)", nullable: false),
                    Tipo = table.Column<int>(type: "integer", nullable: false),
                    TransportadoraId = table.Column<Guid>(type: "uuid", nullable: true),
                    UnidadeId = table.Column<Guid>(type: "uuid", nullable: false),
                    DataCadastro = table.Column<DateTime>(type: "timestamp without time zone", nullable: false),
                    Status = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Veiculos", x => x.VeiculoId);
                });

            migrationBuilder.CreateTable(
                name: "AspNetRoleClaims",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    RoleId = table.Column<string>(type: "text", nullable: false),
                    ClaimType = table.Column<string>(type: "text", nullable: true),
                    ClaimValue = table.Column<string>(type: "text", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AspNetRoleClaims", x => x.Id);
                    table.ForeignKey(
                        name: "FK_AspNetRoleClaims_AspNetRoles_RoleId",
                        column: x => x.RoleId,
                        principalTable: "AspNetRoles",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "AspNetUserClaims",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    UserId = table.Column<string>(type: "text", nullable: false),
                    ClaimType = table.Column<string>(type: "text", nullable: true),
                    ClaimValue = table.Column<string>(type: "text", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AspNetUserClaims", x => x.Id);
                    table.ForeignKey(
                        name: "FK_AspNetUserClaims_AspNetUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "AspNetUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "AspNetUserLogins",
                columns: table => new
                {
                    LoginProvider = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    ProviderKey = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    ProviderDisplayName = table.Column<string>(type: "text", nullable: true),
                    UserId = table.Column<string>(type: "text", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AspNetUserLogins", x => new { x.LoginProvider, x.ProviderKey });
                    table.ForeignKey(
                        name: "FK_AspNetUserLogins_AspNetUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "AspNetUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "AspNetUserRoles",
                columns: table => new
                {
                    UserId = table.Column<string>(type: "text", nullable: false),
                    RoleId = table.Column<string>(type: "text", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AspNetUserRoles", x => new { x.UserId, x.RoleId });
                    table.ForeignKey(
                        name: "FK_AspNetUserRoles_AspNetRoles_RoleId",
                        column: x => x.RoleId,
                        principalTable: "AspNetRoles",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_AspNetUserRoles_AspNetUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "AspNetUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "AspNetUserTokens",
                columns: table => new
                {
                    UserId = table.Column<string>(type: "text", nullable: false),
                    LoginProvider = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    Name = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    Value = table.Column<string>(type: "text", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AspNetUserTokens", x => new { x.UserId, x.LoginProvider, x.Name });
                    table.ForeignKey(
                        name: "FK_AspNetUserTokens_AspNetUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "AspNetUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Anexo",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    MovimentoPortariaId = table.Column<Guid>(type: "uuid", nullable: false),
                    Estagio = table.Column<int>(type: "integer", nullable: false),
                    Url = table.Column<string>(type: "varchar(1000)", nullable: false),
                    TamanhoBytes = table.Column<long>(type: "bigint", nullable: false),
                    ContentType = table.Column<string>(type: "varchar(100)", nullable: false),
                    UsuarioUploadId = table.Column<string>(type: "varchar(450)", nullable: false),
                    Quando = table.Column<DateTime>(type: "timestamp without time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Anexo", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Anexo_MovimentosPortaria_MovimentoPortariaId",
                        column: x => x.MovimentoPortariaId,
                        principalTable: "MovimentosPortaria",
                        principalColumn: "MovimentoPortariaId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "EventoFluxo",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    MovimentoPortariaId = table.Column<Guid>(type: "uuid", nullable: false),
                    Tipo = table.Column<int>(type: "integer", nullable: false),
                    DeEstado = table.Column<int>(type: "integer", nullable: true),
                    ParaEstado = table.Column<int>(type: "integer", nullable: true),
                    UsuarioId = table.Column<string>(type: "varchar(450)", nullable: false),
                    Quando = table.Column<DateTime>(type: "timestamp without time zone", nullable: false),
                    Detalhes = table.Column<string>(type: "varchar(2000)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_EventoFluxo", x => x.Id);
                    table.ForeignKey(
                        name: "FK_EventoFluxo_MovimentosPortaria_MovimentoPortariaId",
                        column: x => x.MovimentoPortariaId,
                        principalTable: "MovimentosPortaria",
                        principalColumn: "MovimentoPortariaId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "NotificacaoPendente",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    MovimentoPortariaId = table.Column<Guid>(type: "uuid", nullable: false),
                    Canal = table.Column<int>(type: "integer", nullable: false),
                    Destino = table.Column<string>(type: "varchar(500)", nullable: false),
                    Payload = table.Column<string>(type: "text", nullable: false),
                    Status = table.Column<int>(type: "integer", nullable: false),
                    Tentativas = table.Column<int>(type: "integer", nullable: false),
                    ProximaTentativa = table.Column<DateTime>(type: "timestamp without time zone", nullable: true),
                    UltimoErro = table.Column<string>(type: "varchar(2000)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_NotificacaoPendente", x => x.Id);
                    table.ForeignKey(
                        name: "FK_NotificacaoPendente_MovimentosPortaria_MovimentoPortariaId",
                        column: x => x.MovimentoPortariaId,
                        principalTable: "MovimentosPortaria",
                        principalColumn: "MovimentoPortariaId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Anexo_MovimentoPortariaId_Estagio",
                table: "Anexo",
                columns: new[] { "MovimentoPortariaId", "Estagio" });

            migrationBuilder.CreateIndex(
                name: "IX_AspNetRoleClaims_RoleId",
                table: "AspNetRoleClaims",
                column: "RoleId");

            migrationBuilder.CreateIndex(
                name: "RoleNameIndex",
                table: "AspNetRoles",
                column: "NormalizedName",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_AspNetUserClaims_UserId",
                table: "AspNetUserClaims",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_AspNetUserLogins_UserId",
                table: "AspNetUserLogins",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_AspNetUserRoles_RoleId",
                table: "AspNetUserRoles",
                column: "RoleId");

            migrationBuilder.CreateIndex(
                name: "EmailIndex",
                table: "AspNetUsers",
                column: "NormalizedEmail");

            migrationBuilder.CreateIndex(
                name: "UserNameIndex",
                table: "AspNetUsers",
                column: "NormalizedUserName",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_EventoFluxo_MovimentoPortariaId_Quando",
                table: "EventoFluxo",
                columns: new[] { "MovimentoPortariaId", "Quando" });

            migrationBuilder.CreateIndex(
                name: "IX_MovimentosPortaria_UnidadeId_CarretaId_Estado",
                table: "MovimentosPortaria",
                columns: new[] { "UnidadeId", "CarretaId", "Estado" });

            migrationBuilder.CreateIndex(
                name: "IX_MovimentosPortaria_UnidadeId_Estado_DataChegada",
                table: "MovimentosPortaria",
                columns: new[] { "UnidadeId", "Estado", "DataChegada" });

            migrationBuilder.CreateIndex(
                name: "IX_NotificacaoPendente_MovimentoPortariaId",
                table: "NotificacaoPendente",
                column: "MovimentoPortariaId");

            migrationBuilder.CreateIndex(
                name: "IX_NotificacaoPendente_Status_ProximaTentativa",
                table: "NotificacaoPendente",
                columns: new[] { "Status", "ProximaTentativa" });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Anexo");

            migrationBuilder.DropTable(
                name: "AspNetRoleClaims");

            migrationBuilder.DropTable(
                name: "AspNetUserClaims");

            migrationBuilder.DropTable(
                name: "AspNetUserLogins");

            migrationBuilder.DropTable(
                name: "AspNetUserRoles");

            migrationBuilder.DropTable(
                name: "AspNetUserTokens");

            migrationBuilder.DropTable(
                name: "EventoFluxo");

            migrationBuilder.DropTable(
                name: "Motoristas");

            migrationBuilder.DropTable(
                name: "NotificacaoPendente");

            migrationBuilder.DropTable(
                name: "Portarias");

            migrationBuilder.DropTable(
                name: "RefreshTokens");

            migrationBuilder.DropTable(
                name: "SecurityKeys");

            migrationBuilder.DropTable(
                name: "Transportadoras");

            migrationBuilder.DropTable(
                name: "Unidades");

            migrationBuilder.DropTable(
                name: "Veiculos");

            migrationBuilder.DropTable(
                name: "AspNetRoles");

            migrationBuilder.DropTable(
                name: "AspNetUsers");

            migrationBuilder.DropTable(
                name: "MovimentosPortaria");
        }
    }
}
