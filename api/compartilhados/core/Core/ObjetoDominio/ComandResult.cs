using System.Text;
using System.Text.Json;

namespace Core.ObjetoDominio
{
    public class ComandResult : IComandResult
    {
        public ComandResult()
        {
            
        }
        public ComandResult(bool success, string message, dynamic data,int code = 400)
        {
            Success = success;
            Message = message;
            Data = data;
            Code = code;
        }

        public bool Success { get; set; }
        public string? Message { get; set; }
        public object? Data { get; set; }
        public int? Code { get; set; } = 400;

        public async Task<T> GetData<T>()
        {
            if (Success && Data != null)
            {
                var jsonDados = JsonSerializer.Serialize(Data);
                //var conteudo = new StringContent(jsonDados, Encoding.UTF8, "application/json");
                var retorno =  JsonSerializer.Deserialize<T>(jsonDados.ToString(),
                         new JsonSerializerOptions
                         {
                             PropertyNameCaseInsensitive = true
                         });

                return retorno;
            }
            else
            {
                throw new InvalidOperationException("Data is null or Success is false.");
            }
        }

        public async Task<List<T>> GetListData<T>()
        {
            if (Data != null)
            {
                var jsonDados = JsonSerializer.Serialize(Data);
                //var conteudo = new StringContent(jsonDados, Encoding.UTF8, "application/json");
                var retorno = JsonSerializer.Deserialize<List<T>>(jsonDados.ToString(),
                         new JsonSerializerOptions
                         {
                             PropertyNameCaseInsensitive = true
                         });

                return retorno;
            }
            else
            {
                throw new InvalidOperationException("Data is null or Success is false.");
            }
        }


    }
}
