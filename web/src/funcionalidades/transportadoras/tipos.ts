import { z } from "zod";

export const transportadoraSchema = z.object({
  transportadoraId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarTransportadoraSchema = transportadoraSchema.omit({ transportadoraId: true });
export const alterarTransportadoraSchema = transportadoraSchema;

export type Transportadora = z.infer<typeof transportadoraSchema>;
export type SalvarTransportadora = z.infer<typeof salvarTransportadoraSchema>;
export type AlterarTransportadora = z.infer<typeof alterarTransportadoraSchema>;

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
