using System.Net;

namespace Core.Exeptions;

public class DominioException : ApiException
{
    public DominioException(string message) : base(message, HttpStatusCode.BadRequest) { }
}

public class NaoEncontradoException : ApiException
{
    public NaoEncontradoException(string recurso) : base($"{recurso} nao encontrado", HttpStatusCode.NotFound) { }
}

public class NaoAutorizadoException : ApiException
{
    public NaoAutorizadoException(string message = "Nao autorizado") : base(message, HttpStatusCode.Unauthorized) { }
}

public class ConflitoException : ApiException
{
    public ConflitoException(string message) : base(message, HttpStatusCode.Conflict) { }
}
