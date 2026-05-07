using Core.ObjetoDominio;
using System.Net;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;

namespace Core.Services
{
    public abstract class BaseApiService
    {
        protected readonly HttpClient _httpClient;

        protected BaseApiService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        protected async Task<T?> ObterDadosAsync<T>(string endpoint, Dictionary<string, string>? headers = null)
        {
            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                };

                AddHeaders(headers);

                return await _httpClient.GetFromJsonAsync<T>($"{endpoint}", options);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Erro durante a solicitação GET: {ex.Message}");
                return default;
            }
        }



        protected async Task<(TResposta?, HttpStatusCode?, string)> EnviarDadosAsync<TResposta, TDados>(string endpoint, HttpMethod metodo, TDados dados, Dictionary<string, string>? headers = null)
        {
            try
            {
                StringContent conteudo = Seralizar(dados);

                AddHeaders(headers);
                HttpResponseMessage response = await Response(endpoint, metodo, conteudo);
                var responseData = await ExtrairResponse<TResposta>(response);

                return (default, response.StatusCode, "ok");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Erro durante a solicitação: {ex.Message}");
                return (default, null, ex.Message);
            }
        }

        private static StringContent Seralizar<TDados>(TDados dados)
        {
            var jsonDados = JsonSerializer.Serialize(dados);
            var conteudo = new StringContent(jsonDados, Encoding.UTF8, "application/json");
            return conteudo;
        }

        protected async Task<ComandResult?> Upload<TDados>(string endpoint, HttpMethod metodo, MultipartFormDataContent dados, Dictionary<string, string>? headers = null)
        {
            try
            {
                       

                AddHeaders(headers);
                HttpResponseMessage response = await ResponseUpload(endpoint, metodo, dados);
                var responseData = await ExtrairResponse<ComandResult>(response);

                return responseData;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Erro durante a solicitação: {ex.Message}");
                return new ComandResult(false, "Erro durante a solicitação: {ex.Message}", new List<string>());
            }
        }
        protected async Task<ComandResult?> EnviarDadosAsync2<TDados>(string endpoint, HttpMethod metodo, TDados dados, Dictionary<string, string>? headers = null)
        {
            try
            {

                StringContent conteudo = Seralizar(dados);

                AddHeaders(headers);
                HttpResponseMessage response = await Response(endpoint, metodo, conteudo);
                var responseData = await ExtrairResponse<ComandResult>(response);

                return responseData;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Erro durante a solicitação: {ex.Message}");
                return new ComandResult(false, "Erro durante a solicitação: {ex.Message}",new List<string>());
            }
        }

        private static async Task<TResposta?> ExtrairResponse<TResposta>(HttpResponseMessage response)
        {
            var responseContent = await response.Content.ReadAsStringAsync();
            var responseData = JsonSerializer.Deserialize<TResposta>(responseContent, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
            return responseData;
        }

        private async Task<HttpResponseMessage> Response(string endpoint, HttpMethod metodo, StringContent conteudo)
        {
            HttpResponseMessage response;

            if (metodo == HttpMethod.Post)
            {
                response = await _httpClient.PostAsync($"{endpoint}", conteudo);
            }
            else if (metodo == HttpMethod.Put)
            {
                response = await _httpClient.PutAsync($"{endpoint}", conteudo);
            }
            else if (metodo == HttpMethod.Get)
            {
                response = await _httpClient.GetAsync($"{endpoint}");
            }
            else if (metodo == HttpMethod.Delete)
            {
                response = await _httpClient.DeleteAsync($"{endpoint}");
            }
            else
            {
                response = new HttpResponseMessage(HttpStatusCode.MethodNotAllowed);
            }

            return response;
        }

        //private List<string> Mapear(ComandResult comand)
        //{

        //}

        private async Task<HttpResponseMessage> ResponseUpload(string endpoint, HttpMethod metodo, MultipartFormDataContent conteudo)
        {
            HttpResponseMessage response;

            if (metodo == HttpMethod.Post)
            {
                response = await _httpClient.PostAsync($"{endpoint}", conteudo);
            }
            else if (metodo == HttpMethod.Put)
            {
                response = await _httpClient.PutAsync($"{endpoint}", conteudo);
            }
            else if (metodo == HttpMethod.Get)
            {
                response = await _httpClient.GetAsync($"{endpoint}");
            }
            else if (metodo == HttpMethod.Delete)
            {
                response = await _httpClient.DeleteAsync($"{endpoint}");
            }
            else
            {
                response = new HttpResponseMessage(HttpStatusCode.MethodNotAllowed);
            }

            return response;
        }
        private void AddHeaders(Dictionary<string, string>? headers)
        {
            _httpClient.DefaultRequestHeaders.Clear();

            if (headers != null)
            {
                foreach (var header in headers)
                {
                    _httpClient.DefaultRequestHeaders.Add(header.Key, header.Value);
                }
            }
        }
    }

}
