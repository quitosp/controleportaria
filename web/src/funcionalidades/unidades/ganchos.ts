import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarUnidades, salvarUnidade, alterarUnidade } from "./api";
import type { SalvarUnidade, AlterarUnidade } from "./tipos";

const CHAVE = ["unidades"] as const;

export function useListarUnidades(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarUnidades(pageIndex, pageSize, filter),
  });
}

export function useSalvarUnidade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarUnidade) => salvarUnidade(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarUnidade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarUnidade) => alterarUnidade(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
