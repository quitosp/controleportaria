using Core.ObjetoDominio;

namespace BlazorApp.Shareds.Models
{
    public class ComandResponse
    {
        // Root myDeserializedClass = JsonConvert.DeserializeObject<Root>(myJsonResponse);
       

       
            public bool Success { get; set; }
            public string? Message { get; set; }
            public Data? data { get; set; }
            public int? Code { get; set; }
        


    }
}
