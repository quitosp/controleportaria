import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarConfirmarEntradas, salvarConfirmarEntrada, alterarConfirmarEntrada } from "./api";
import type { SalvarConfirmarEntrada, AlterarConfirmarEntrada } from "./tipos";

const CHAVE = ["confirmar-entrada"] as const;

export function useListarConfirmarEntradas(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarConfirmarEntradas(pageIndex, pageSize, filter),
  });
}

export function useSalvarConfirmarEntrada() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarConfirmarEntrada) => salvarConfirmarEntrada(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarConfirmarEntrada() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarConfirmarEntrada) => alterarConfirmarEntrada(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
