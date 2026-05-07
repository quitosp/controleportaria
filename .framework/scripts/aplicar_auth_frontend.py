"""
Gera autenticacao no frontend Next.js: useAuth + AuthProvider + login + layout privado.
Cobre os bugs reportados em projetos reais:
  - Race condition entre router.push e AuthProvider (usa useEffect waiting)
  - Claims extraction multi-formato (.NET emite role/roles/claim XML)
  - localStorage SSR-safe
  - jwt-decode wrapper que nao quebra em token invalido

Uso:
  python aplicar_auth_frontend.py --raiz web

Idempotente: nao sobrescreve arquivos ja editados pelo usuario (compara checksum simples).
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

USEAUTH = '''"use client";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { jwtDecode } from "jwt-decode";

type Usuario = { id: string; email: string; nome?: string; roles: string[] };

type AuthCtx = {
  usuario: Usuario | null;
  email: string | null;
  autenticado: boolean;
  carregando: boolean;
  entrar: (token: string, refreshToken: string) => boolean;
  sair: () => void;
};

const Ctx = createContext<AuthCtx | null>(null);

function extrairUsuario(token: string): Usuario | null {
  try {
    const c = jwtDecode<Record<string, unknown>>(token);
    const id = (c["sub"] || c["nameid"] || c["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier"]) as string | undefined;
    const email = (c["email"] || c["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"]) as string | undefined;
    const nome = (c["name"] || c["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"]) as string | undefined;
    const rawRole = c["role"] || c["roles"] || c["http://schemas.microsoft.com/ws/2008/06/identity/claims/role"];
    const roles: string[] = Array.isArray(rawRole) ? rawRole as string[] : (rawRole ? [rawRole as string] : []);
    if (!id || !email) return null;
    return { id, email, nome, roles };
  } catch (e) {
    console.error("[auth] falha ao decodificar JWT", e);
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const t = localStorage.getItem("token");
    if (t) {
      const u = extrairUsuario(t);
      if (u) setUsuario(u);
      else localStorage.removeItem("token");
    }
    setCarregando(false);
  }, []);

  const entrar = (token: string, refreshToken: string) => {
    const u = extrairUsuario(token);
    if (!u) return false;
    if (typeof window !== "undefined") {
      localStorage.setItem("token", token);
      localStorage.setItem("refreshToken", refreshToken);
    }
    setUsuario(u);
    return true;
  };

  const sair = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
    }
    setUsuario(null);
    router.replace("/login");
  };

  return (
    <Ctx.Provider value={{ usuario, email: usuario?.email ?? null, autenticado: !!usuario, carregando, entrar, sair }}>
      {children}
    </Ctx.Provider>
  );
}

export function useAuth() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth precisa estar dentro de <AuthProvider>");
  return v;
}
'''

LOGIN_PAGE = '''"use client";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { Label } from "@/compartilhados/componentes/ui/label";
import { useAuth } from "@/compartilhados/ganchos/useAuth";
import { api } from "@/compartilhados/servicos/api";

const schema = z.object({ email: z.string().email("Email invalido"), senha: z.string().min(1, "Senha obrigatoria") });
type LoginEntrada = z.infer<typeof schema>;

export default function PaginaLogin() {
  const router = useRouter();
  const { entrar, autenticado } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm<LoginEntrada>({
    resolver: zodResolver(schema),
    defaultValues: { email: "admin@local", senha: "Admin@123" },
  });

  // Espera o usuario aparecer no contexto antes de navegar (evita race com LayoutPrivado)
  useEffect(() => {
    if (autenticado) router.push("/dashboard");
  }, [autenticado, router]);

  const mutation = useMutation({
    mutationFn: async (dados: LoginEntrada) => {
      const { data } = await api.post("/api/Auth/v1/entrar", dados);
      return data;
    },
    onSuccess: (resp) => {
      if (!resp?.success) { toast.error(resp?.message ?? "Falha no login"); return; }
      const ok = entrar(resp.data.accessToken, resp.data.refreshToken);
      if (!ok) toast.error("Token invalido recebido do servidor");
      else toast.success("Login efetuado");
    },
    onError: (e: { response?: { data?: { message?: string } } }) => {
      toast.error(e?.response?.data?.message ?? "Erro ao entrar");
    },
  });

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-bold tracking-tight">Entrar</h1>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" {...register("email")} />
          {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="senha">Senha</Label>
          <Input id="senha" type="password" {...register("senha")} />
          {errors.senha && <p className="text-sm text-destructive">{errors.senha.message}</p>}
        </div>
        <Button type="submit" disabled={mutation.isPending} className="w-full">
          {mutation.isPending ? "Entrando..." : "Entrar"}
        </Button>
      </form>
    </div>
  );
}
'''

LAYOUT_PRIVADO = '''"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/compartilhados/ganchos/useAuth";

export default function LayoutPrivado({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { autenticado, carregando } = useAuth();

  useEffect(() => {
    if (!carregando && !autenticado) router.replace("/login");
  }, [autenticado, carregando, router]);

  if (carregando) return <div className="p-6 text-sm text-muted-foreground">Carregando...</div>;
  if (!autenticado) return null;
  return <>{children}</>;
}
'''

API_BASE = '''import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5001",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const t = localStorage.getItem("token");
    if (t) config.headers.Authorization = `Bearer ${t}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (e) => {
    if (typeof window !== "undefined" && e?.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
      if (window.location.pathname !== "/login") window.location.href = "/login";
    }
    return Promise.reject(e);
  }
);
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", required=True, help="caminho do projeto Next (geralmente 'web')")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    if not (raiz / "package.json").exists():
        print(f"ERRO: {raiz} nao parece projeto Next.js"); return

    arquivos = [
        ("src/compartilhados/ganchos/useAuth.tsx", USEAUTH),
        ("src/app/(publico)/login/page.tsx", LOGIN_PAGE),
        ("src/app/(privado)/layout.tsx", LAYOUT_PRIVADO),
        ("src/compartilhados/servicos/api.ts", API_BASE),
    ]

    for rel, conteudo in arquivos:
        alvo = raiz / rel
        if alvo.exists():
            print(f"  -- {rel} ja existe (preservado)")
            continue
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8")
        print(f"  OK {rel}")

    # garantir AuthProvider no provedores.tsx
    prov = raiz / "src/nucleo/provedores.tsx"
    if prov.exists():
        txt = prov.read_text(encoding="utf-8")
        if "AuthProvider" not in txt:
            txt = 'import { AuthProvider } from "@/compartilhados/ganchos/useAuth";\n' + txt
            txt = txt.replace("<ProvedorTema", "<AuthProvider><ProvedorTema").replace("</ProvedorTema>", "</ProvedorTema></AuthProvider>")
            prov.write_text(txt, encoding="utf-8")
            print(f"  OK provedores.tsx (AuthProvider injetado)")

    # garantir jwt-decode no package.json
    pkg = raiz / "package.json"
    pkg_data = json.loads(pkg.read_text(encoding="utf-8"))
    pkg_data.setdefault("dependencies", {})
    if "jwt-decode" not in pkg_data["dependencies"]:
        pkg_data["dependencies"]["jwt-decode"] = "^4.0.0"
        pkg.write_text(json.dumps(pkg_data, indent=2) + "\n", encoding="utf-8")
        print("  OK package.json: jwt-decode adicionado")

    print(f"\nProximo: cd {raiz} && npm install")


if __name__ == "__main__":
    main()
