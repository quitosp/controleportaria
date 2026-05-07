import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarPainelChamadas, salvarPainelChamada, alterarPainelChamada } from "./api";
import type { SalvarPainelChamada, AlterarPainelChamada } from "./tipos";

const CHAVE = ["painel-chamada"] as const;

export function useListarPainelChamadas(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarPainelChamadas(pageIndex, pageSize, filter),
  });
}

export function useSalvarPainelChamada() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarPainelChamada) => salvarPainelChamada(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarPainelChamada() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarPainelChamada) => alterarPainelChamada(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
