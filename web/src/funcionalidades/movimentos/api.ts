import { api } from "@/compartilhados/servicos/api";
import type { Movimento, SalvarMovimento, AlterarMovimento, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/movimento/v1";

export async function listarMovimentos(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<Movimento>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarMovimento(payload: SalvarMovimento) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarMovimento(payload: AlterarMovimento) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
