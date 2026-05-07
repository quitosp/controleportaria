import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarTransportadoras, salvarTransportadora, alterarTransportadora } from "./api";
import type { SalvarTransportadora, AlterarTransportadora } from "./tipos";

const CHAVE = ["transportadoras"] as const;

export function useListarTransportadoras(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarTransportadoras(pageIndex, pageSize, filter),
  });
}

export function useSalvarTransportadora() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarTransportadora) => salvarTransportadora(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarTransportadora() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarTransportadora) => alterarTransportadora(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
