import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarLogins, salvarLogin, alterarLogin } from "./api";
import type { SalvarLogin, AlterarLogin } from "./tipos";

const CHAVE = ["login"] as const;

export function useListarLogins(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarLogins(pageIndex, pageSize, filter),
  });
}

export function useSalvarLogin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarLogin) => salvarLogin(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarLogin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarLogin) => alterarLogin(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
