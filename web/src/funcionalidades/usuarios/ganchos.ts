import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarUsuarios, salvarUsuario, alterarUsuario } from "./api";
import type { SalvarUsuario, AlterarUsuario } from "./tipos";

const CHAVE = ["usuarios"] as const;

export function useListarUsuarios(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listarUsuarios(pageIndex, pageSize, filter),
  });
}

export function useSalvarUsuario() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarUsuario) => salvarUsuario(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}

export function useAlterarUsuario() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlterarUsuario) => alterarUsuario(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CHAVE }),
  });
}
