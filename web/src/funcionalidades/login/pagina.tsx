"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { Label } from "@/compartilhados/componentes/ui/label";
import { Card } from "@/compartilhados/componentes/ui/card";
import { entrar } from "@/compartilhados/servicos/auth";

export function PaginaLogin() {
  const [email, setEmail] = useState("admin@local");
  const [senha, setSenha] = useState("Admin@123");
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);
  const router = useRouter();

  async function submeter(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setCarregando(true);
    try {
      await entrar(email, senha);
      router.push("/dashboard");
    } catch (ex: any) {
      setErro(ex?.response?.status === 423 ? "Usuario bloqueado por tentativas invalidas" : "Login ou senha invalidos");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md p-6 space-y-5">
        <div>
          <h1 className="text-2xl font-semibold">Acessar o sistema</h1>
          <p className="text-sm text-muted-foreground mt-1">Frigoestrela — Controle de Portaria</p>
        </div>
        <form onSubmit={submeter} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" autoFocus value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="senha">Senha</Label>
            <Input id="senha" type="password" value={senha} onChange={e => setSenha(e.target.value)} required />
          </div>
          {erro && <div className="text-sm text-destructive">{erro}</div>}
          <Button type="submit" className="w-full" disabled={carregando}>
            {carregando ? "Entrando..." : "Entrar"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
