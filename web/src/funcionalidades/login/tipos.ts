import { z } from "zod";

export const loginSchema = z.object({
  loginId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarLoginSchema = loginSchema.omit({ loginId: true });
export const alterarLoginSchema = loginSchema;

export type Login = z.infer<typeof loginSchema>;
export type SalvarLogin = z.infer<typeof salvarLoginSchema>;
export type AlterarLogin = z.infer<typeof alterarLoginSchema>;

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
