import { api } from "@/compartilhados/servicos/api";
import type { Transportadora, SalvarTransportadora, AlterarTransportadora, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/transportadora/v1";

export async function listarTransportadoras(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<Transportadora>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarTransportadora(payload: SalvarTransportadora) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarTransportadora(payload: AlterarTransportadora) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
