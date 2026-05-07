namespace Core.ObjetoDominio
{
    public class Data
    {
        public Data(List<Error> errors)
        {
            
            Errors = errors;
        }

       public List<Error> Errors { get; set; } = new List<Error>();
     
    }

    public class Error
    {
        public Error(string? propertyName, string? errorMessage,string? errorCode)
        {
            PropertyName = propertyName;
            ErrorMessage = errorMessage;
            ErrorCode = errorCode;
           
        }

        public string? PropertyName { get; set; }
        public string? ErrorMessage { get; set; }
        public string? ErrorCode { get; set; }
        
    }

   
}
