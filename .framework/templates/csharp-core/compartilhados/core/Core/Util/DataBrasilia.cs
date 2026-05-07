using System;

namespace Core.Util
{
    public static class DataBrasilia
    {
        public static DateTime HorarioBrasilia()
        {
            DateTime timeUtc = DateTime.UtcNow;
            var brasilia = TimeZoneInfo.FindSystemTimeZoneById("E. South America Standard Time");

            var data = TimeZoneInfo.ConvertTimeFromUtc(timeUtc, brasilia);

            return data;
        }

        public static long DiferencaDataEmMinutos(DateTime data)
        {
            // Calculando a diferença em minutos entre a data atual e $json.last_interaction
            TimeSpan diff = HorarioBrasilia() - data;
            double minutesDifference = diff.TotalMinutes;

            // Arredondando para o número inteiro mais próximo
            long roundedMinutesDifference = (long)Math.Round(minutesDifference);
            return roundedMinutesDifference;
        }
    }

   
}
