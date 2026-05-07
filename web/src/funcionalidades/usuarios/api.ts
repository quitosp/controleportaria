import { api } from "@/compartilhados/servicos/api";
import type { Usuario, SalvarUsuario, AlterarUsuario, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/usuario/v1";

export async function listarUsuarios(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<Usuario>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarUsuario(payload: SalvarUsuario) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarUsuario(payload: AlterarUsuario) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
