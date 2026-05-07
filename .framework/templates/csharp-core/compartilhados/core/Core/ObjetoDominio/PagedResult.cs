namespace Core.ObjetoDominio
{
    public class PagedResult<T> where T : class
    {
        public List<T> List { get; set; }
        public int TotalResults { get; set; }
        public int PageIndex { get; set; }
        public int PageSize { get; set; }
        public string? Query { get; set; }
    }
}
