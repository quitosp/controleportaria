import { z } from "zod";

export const portariaSchema = z.object({
  portariaId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarPortariaSchema = portariaSchema.omit({ portariaId: true });
export const alterarPortariaSchema = portariaSchema;

export type Portaria = z.infer<typeof portariaSchema>;
export type SalvarPortaria = z.infer<typeof salvarPortariaSchema>;
export type AlterarPortaria = z.infer<typeof alterarPortariaSchema>;

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
