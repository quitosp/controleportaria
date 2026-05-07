import { api } from "@/compartilhados/servicos/api";
import type { Portaria, SalvarPortaria, AlterarPortaria, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/portaria/v1";

export async function listarPortarias(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<Portaria>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarPortaria(payload: SalvarPortaria) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarPortaria(payload: AlterarPortaria) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
