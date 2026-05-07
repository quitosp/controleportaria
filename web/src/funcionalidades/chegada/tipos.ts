import { z } from "zod";

export const chegadaSchema = z.object({
  chegadaId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarChegadaSchema = chegadaSchema.omit({ chegadaId: true });
export const alterarChegadaSchema = chegadaSchema;

export type Chegada = z.infer<typeof chegadaSchema>;
export type SalvarChegada = z.infer<typeof salvarChegadaSchema>;
export type AlterarChegada = z.infer<typeof alterarChegadaSchema>;

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
