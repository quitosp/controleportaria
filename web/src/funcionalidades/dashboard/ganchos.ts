import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarDashboards, salvarDashboard, alterarDashboard } from "./api";
import type { SalvarDashboard, AlterarDashboard } from "./tipos";

const CHAVE = ["dashboard"] as const;

export function useListarDashboards(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarDashboards(pageIndex, pageSize, filter),
  });
}

export function useSalvarDashboard() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarDashboard) => salvarDashboard(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarDashboard() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarDashboard) => alterarDashboard(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
