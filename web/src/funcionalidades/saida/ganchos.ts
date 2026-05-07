import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarSaidas, salvarSaida, alterarSaida } from "./api";
import type { SalvarSaida, AlterarSaida } from "./tipos";

const CHAVE = ["saida"] as const;

export function useListarSaidas(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarSaidas(pageIndex, pageSize, filter),
  });
}

export function useSalvarSaida() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarSaida) => salvarSaida(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarSaida() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarSaida) => alterarSaida(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
