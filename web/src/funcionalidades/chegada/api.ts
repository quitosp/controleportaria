import { api } from "@/compartilhados/servicos/api";
import type { Chegada, SalvarChegada, AlterarChegada, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/chegada/v1";

export async function listarChegadas(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<Chegada>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarChegada(payload: SalvarChegada) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarChegada(payload: AlterarChegada) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
