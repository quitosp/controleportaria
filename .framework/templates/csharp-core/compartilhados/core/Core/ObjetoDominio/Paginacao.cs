namespace Core.ObjetoDominio
{
    public class Paginacao
    {
        public Paginacao()
        {
            
        }
        public Paginacao(int pagina, int quantidadePorPagina, bool status)
        {
            Pagina = pagina;
            QuantidadePorPagina = quantidadePorPagina;
            Status = status;
        }

        public int Pagina { get; set; }
        public int QuantidadePorPagina { get; set; }
        public bool Status { get; set; } = true;
    }
}
