import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarPortarias, salvarPortaria, alterarPortaria } from "./api";
import type { SalvarPortaria, AlterarPortaria } from "./tipos";

const CHAVE = ["portarias"] as const;

export function useListarPortarias(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarPortarias(pageIndex, pageSize, filter),
  });
}

export function useSalvarPortaria() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarPortaria) => salvarPortaria(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarPortaria() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarPortaria) => alterarPortaria(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
