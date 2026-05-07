import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarMotoristas, salvarMotorista, alterarMotorista } from "./api";
import type { SalvarMotorista, AlterarMotorista } from "./tipos";

const CHAVE = ["motoristas"] as const;

export function useListarMotoristas(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarMotoristas(pageIndex, pageSize, filter),
  });
}

export function useSalvarMotorista() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarMotorista) => salvarMotorista(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarMotorista() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarMotorista) => alterarMotorista(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
