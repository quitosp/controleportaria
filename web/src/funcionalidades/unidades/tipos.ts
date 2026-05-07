import { z } from "zod";

export const unidadeSchema = z.object({
  unidadeId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarUnidadeSchema = unidadeSchema.omit({ unidadeId: true });
export const alterarUnidadeSchema = unidadeSchema;

export type Unidade = z.infer<typeof unidadeSchema>;
export type SalvarUnidade = z.infer<typeof salvarUnidadeSchema>;
export type AlterarUnidade = z.infer<typeof alterarUnidadeSchema>;

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
