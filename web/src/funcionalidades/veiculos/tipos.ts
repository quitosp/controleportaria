import { z } from "zod";

export const veiculoSchema = z.object({
  veiculoId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarVeiculoSchema = veiculoSchema.omit({ veiculoId: true });
export const alterarVeiculoSchema = veiculoSchema;

export type Veiculo = z.infer<typeof veiculoSchema>;
export type SalvarVeiculo = z.infer<typeof salvarVeiculoSchema>;
export type AlterarVeiculo = z.infer<typeof alterarVeiculoSchema>;

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
