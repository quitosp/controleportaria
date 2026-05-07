import { z } from "zod";

export const movimentoSchema = z.object({
  movimentoId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarMovimentoSchema = movimentoSchema.omit({ movimentoId: true });
export const alterarMovimentoSchema = movimentoSchema;

export type Movimento = z.infer<typeof movimentoSchema>;
export type SalvarMovimento = z.infer<typeof salvarMovimentoSchema>;
export type AlterarMovimento = z.infer<typeof alterarMovimentoSchema>;

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
