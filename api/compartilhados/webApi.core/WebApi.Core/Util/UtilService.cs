using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WebApi.Core.Util
{
    public static class UtilService
    {
        public static string ExtrairNumeroTelefone(string input)
        {
          

            // Iterar pela string e pegar somente os dígitos
            string numero = "";
            foreach (char c in input)
            {
                if (char.IsDigit(c))
                {
                    numero += c;
                }
            }

            return numero;
        }
    }
}
