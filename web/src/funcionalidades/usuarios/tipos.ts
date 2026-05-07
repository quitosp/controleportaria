import { z } from "zod";

export const usuarioSchema = z.object({
  usuarioId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarUsuarioSchema = usuarioSchema.omit({ usuarioId: true });
export const alterarUsuarioSchema = usuarioSchema;

export type Usuario = z.infer<typeof usuarioSchema>;
export type SalvarUsuario = z.infer<typeof salvarUsuarioSchema>;
export type AlterarUsuario = z.infer<typeof alterarUsuarioSchema>;

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
