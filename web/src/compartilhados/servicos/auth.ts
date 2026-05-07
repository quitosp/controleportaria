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
  if (!data?.Sucesso && !data?.sucesso) {
    throw new Error(data?.Mensagem || data?.mensagem || "Falha no login");
  }
  const dados = data?.Data || data?.data;
  const token = dados?.AccessToken || dados?.accessToken;
  const refresh = dados?.RefreshToken || dados?.refreshToken;
  if (!token) throw new Error("Token nao retornado");
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
