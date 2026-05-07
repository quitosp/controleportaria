import { z } from "zod";

export const motoristaSchema = z.object({
  motoristaId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarMotoristaSchema = motoristaSchema.omit({ motoristaId: true });
export const alterarMotoristaSchema = motoristaSchema;

export type Motorista = z.infer<typeof motoristaSchema>;
export type SalvarMotorista = z.infer<typeof salvarMotoristaSchema>;
export type AlterarMotorista = z.infer<typeof alterarMotoristaSchema>;

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
