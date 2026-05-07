import { z } from "zod";

export const painelchamadaSchema = z.object({
  painelchamadaId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarPainelChamadaSchema = painelchamadaSchema.omit({ painelchamadaId: true });
export const alterarPainelChamadaSchema = painelchamadaSchema;

export type PainelChamada = z.infer<typeof painelchamadaSchema>;
export type SalvarPainelChamada = z.infer<typeof salvarPainelChamadaSchema>;
export type AlterarPainelChamada = z.infer<typeof alterarPainelChamadaSchema>;

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
