import { jwtDecode } from "jwt-decode";
import { api } from "./api";

export type Papel = "Porteiro" | "Lider" | "Supervisor" | "Admin";

export interface SessaoUsuario {
  sub: string;
  email: string;
  name: string;
  papel: Papel;
  unidadeId?: string;
  portariaPadraoId?: string;
  exp: number;
}

const KEY = "auth.token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(KEY);
}

export function getSessao(): SessaoUsuario | null {
  const t = getToken();
  if (!t) return null;
  try {
    const data = jwtDecode<any>(t);
    if (data.exp * 1000 < Date.now()) return null;
    return data as SessaoUsuario;
  } catch {
    return null;
  }
}

export function papelMaiorOuIgual(atual: Papel | undefined, minimo: Papel): boolean {
  const ordem: Record<Papel, number> = { Porteiro: 0, Lider: 1, Supervisor: 2, Admin: 3 };
  if (!atual) return false;
  return ordem[atual] >= ordem[minimo];
}

export async function entrar(email: string, senha: string) {
  const { data } = await api.post<any>("/api/auth/v1/entrar", { Email: email, Senha: senha });
  // ComandResult: { success, message, data: { accessToken, refreshToken, expiresIn, usuarioToken }, code }
  const sucesso = data?.success ?? data?.Success;
  if (!sucesso) {
    throw new Error(data?.message ?? data?.Message ?? "Falha no login");
  }
  const dados = data?.data ?? data?.Data;
  const token = dados?.accessToken ?? dados?.AccessToken;
  const refresh = dados?.refreshToken ?? dados?.RefreshToken;
  if (!token) throw new Error("Token nao retornado pela API");
  if (typeof window !== "undefined") {
    localStorage.setItem(KEY, token);
    if (refresh) localStorage.setItem("auth.refresh", refresh);
  }
  return getSessao();
}

export function sair() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(KEY);
  localStorage.removeItem("auth.refresh");
  window.location.href = "/login";
}
