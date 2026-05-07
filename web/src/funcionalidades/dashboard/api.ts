import { api } from "@/compartilhados/servicos/api";
import type { Dashboard, SalvarDashboard, AlterarDashboard, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/dashboard/v1";

export async function listarDashboards(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<Dashboard>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarDashboard(payload: SalvarDashboard) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarDashboard(payload: AlterarDashboard) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
