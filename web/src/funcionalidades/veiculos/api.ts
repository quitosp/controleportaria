import { api } from "@/compartilhados/servicos/api";
import type { Veiculo, SalvarVeiculo, AlterarVeiculo, ResultadoPaginado, ComandResult, SalvarResultado } from "./tipos";

const BASE = "/api/veiculo/v1";

export async function listarVeiculos(pageIndex = 1, pageSize = 20, filter?: string) {
  const { data } = await api.get<ResultadoPaginado<Veiculo>>(`${BASE}/listar/${pageIndex}/${pageSize}`, {
    params: filter ? { filter } : undefined,
  });
  return data;
}

export async function salvarVeiculo(payload: SalvarVeiculo) {
  const { data } = await api.post<ComandResult<SalvarResultado>>(`${BASE}/salvar`, payload);
  return data;
}

export async function alterarVeiculo(payload: AlterarVeiculo) {
  const { data } = await api.put<ComandResult<SalvarResultado>>(`${BASE}/alterar`, payload);
  return data;
}
