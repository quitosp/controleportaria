import { z } from "zod";

export const confirmarentradaSchema = z.object({
  confirmarentradaId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarConfirmarEntradaSchema = confirmarentradaSchema.omit({ confirmarentradaId: true });
export const alterarConfirmarEntradaSchema = confirmarentradaSchema;

export type ConfirmarEntrada = z.infer<typeof confirmarentradaSchema>;
export type SalvarConfirmarEntrada = z.infer<typeof salvarConfirmarEntradaSchema>;
export type AlterarConfirmarEntrada = z.infer<typeof alterarConfirmarEntradaSchema>;

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
