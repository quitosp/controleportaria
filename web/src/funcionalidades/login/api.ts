import { api } from "@/compartilhados/servicos/api";
import type { Login, SalvarLogin, AlterarLogin, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/login/v1";

export async function listarLogins(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<Login>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarLogin(payload: SalvarLogin) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarLogin(payload: AlterarLogin) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
