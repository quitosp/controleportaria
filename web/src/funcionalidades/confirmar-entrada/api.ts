import { api } from "@/compartilhados/servicos/api";
import type { ConfirmarEntrada, SalvarConfirmarEntrada, AlterarConfirmarEntrada, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/confirmarentrada/v1";

export async function listarConfirmarEntradas(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<ConfirmarEntrada>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarConfirmarEntrada(payload: SalvarConfirmarEntrada) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarConfirmarEntrada(payload: AlterarConfirmarEntrada) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
