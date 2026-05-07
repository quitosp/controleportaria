import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarVeiculos, salvarVeiculo, alterarVeiculo } from "./api";
import type { SalvarVeiculo, AlterarVeiculo } from "./tipos";

const CHAVE = ["veiculos"] as const;

export function useListarVeiculos(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarVeiculos(pageIndex, pageSize, filter),
  });
}

export function useSalvarVeiculo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarVeiculo) => salvarVeiculo(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarVeiculo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarVeiculo) => alterarVeiculo(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
