import { api } from "@/compartilhados/servicos/api";
import type { Saida, SalvarSaida, AlterarSaida, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/saida/v1";

export async function listarSaidas(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<Saida>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarSaida(payload: SalvarSaida) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarSaida(payload: AlterarSaida) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
