import { api } from "@/compartilhados/servicos/api";
import type { Motorista, SalvarMotorista, AlterarMotorista, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/motorista/v1";

export async function listarMotoristas(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<Motorista>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarMotorista(payload: SalvarMotorista) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarMotorista(payload: AlterarMotorista) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
