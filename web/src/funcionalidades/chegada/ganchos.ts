import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarChegadas, salvarChegada, alterarChegada } from "./api";
import type { SalvarChegada, AlterarChegada } from "./tipos";

const CHAVE = ["chegada"] as const;

export function useListarChegadas(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarChegadas(pageIndex, pageSize, filter),
  });
}

export function useSalvarChegada() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarChegada) => salvarChegada(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarChegada() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarChegada) => alterarChegada(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
