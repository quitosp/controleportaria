import { api } from "@/compartilhados/servicos/api";
import type { PainelChamada, SalvarPainelChamada, AlterarPainelChamada, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/painelchamada/v1";

export async function listarPainelChamadas(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<PainelChamada>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarPainelChamada(payload: SalvarPainelChamada) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarPainelChamada(payload: AlterarPainelChamada) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
