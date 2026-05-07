import { z } from "zod";

export const dashboardSchema = z.object({
  dashboardId: z.string().uuid(),
  nome: z.string().min(1, "Obrigatorio"),
});

export const salvarDashboardSchema = dashboardSchema.omit({ dashboardId: true });
export const alterarDashboardSchema = dashboardSchema;

export type Dashboard = z.infer<typeof dashboardSchema>;
export type SalvarDashboard = z.infer<typeof salvarDashboardSchema>;
export type AlterarDashboard = z.infer<typeof alterarDashboardSchema>;

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
