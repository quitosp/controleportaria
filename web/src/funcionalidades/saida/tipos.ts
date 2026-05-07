import { z } from "zod";

export const saidaSchema = z.object({
  saidaId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarSaidaSchema = saidaSchema.omit({ saidaId: true });
export const alterarSaidaSchema = saidaSchema;

export type Saida = z.infer<typeof saidaSchema>;
export type SalvarSaida = z.infer<typeof salvarSaidaSchema>;
export type AlterarSaida = z.infer<typeof alterarSaidaSchema>;

export type ResultadoPaginado<T> = {
  list: T[];
  totalResults: number;
  pageIndex: number;
  pageSize: number;
  query?: string;
};

export type ComandResult<T = unknown> = {
  success: boolean;
  message: string;
  data: T;
  code: number;
};

export type SalvarResultado = { id: string };
