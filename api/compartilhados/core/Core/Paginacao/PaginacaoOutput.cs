namespace Core.Paginacao
{
    public class PaginacaoOutput<T>
    {
        public List<T>? List { get; set; }
        public int TotalPaginas { get; set; }
        public int TotalRegistro { get; set; } = 0;
    }

}
