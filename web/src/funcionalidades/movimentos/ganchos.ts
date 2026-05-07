import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarMovimentos, salvarMovimento, alterarMovimento } from "./api";
import type { SalvarMovimento, AlterarMovimento } from "./tipos";

const CHAVE = ["movimentos"] as const;

export function useListarMovimentos(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarMovimentos(pageIndex, pageSize, filter),
  });
}

export function useSalvarMovimento() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarMovimento) => salvarMovimento(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarMovimento() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarMovimento) => alterarMovimento(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
