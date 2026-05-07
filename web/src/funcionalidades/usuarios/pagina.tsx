"use client";
import { useEffect, useState } from "react";
import { Card } from "@/compartilhados/componentes/ui/card";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { Label } from "@/compartilhados/componentes/ui/label";
import { Badge } from "@/compartilhados/componentes/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/compartilhados/componentes/ui/dialog";
import { api } from "@/compartilhados/servicos/api";

export function PaginaUsuarios() {
  const [itens, setItens] = useState<any[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [novoOpen, setNovoOpen] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [form, setForm] = useState({ nome: "", email: "", senha: "", confirmacaoSenha: "" });

  async function carregar() {
    setCarregando(true);
    try {
      const r = await api.get("/api/usuarios/v1/listar/1/100");
      setItens(r.data?.list ?? r.data?.List ?? []);
    } finally { setCarregando(false); }
  }

  useEffect(() => { carregar(); }, []);

  async function salvar(e: React.FormEvent) {
    e.preventDefault(); setErro(null);
    if (form.senha !== form.confirmacaoSenha) { setErro("Senhas nao conferem"); return; }
    try {
      await api.post("/api/auth/v1/registrar", form);
      setNovoOpen(false); setForm({ nome: "", email: "", senha: "", confirmacaoSenha: "" });
      carregar();
    } catch (ex: any) {
      setErro(ex?.response?.data?.message ?? "Falha ao registrar");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl">Usuarios</h1>
        <Button onClick={() => setNovoOpen(true)}>Novo usuario</Button>
      </div>
      {erro && <div className="text-sm text-destructive">{erro}</div>}

      <Card className="p-3">
        {carregando && <div>Carregando...</div>}
        <div className="space-y-2">
          {itens.map((u: any) => (
            <div key={u.id} className="flex justify-between items-center p-2 hover:bg-muted rounded">
              <div>
                <div className="font-medium">{u.nome ?? u.userName}</div>
                <div className="text-xs text-muted-foreground">{u.email}</div>
              </div>
              <Badge variant="outline">{u.papel ?? "—"}</Badge>
            </div>
          ))}
        </div>
      </Card>

      <Dialog open={novoOpen} onOpenChange={setNovoOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Novo usuario</DialogTitle></DialogHeader>
          <form onSubmit={salvar} className="space-y-3">
            <div><Label>Nome</Label><Input value={form.nome} onChange={e => setForm({...form, nome: e.target.value})} required /></div>
            <div><Label>Email</Label><Input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required /></div>
            <div><Label>Senha</Label><Input type="password" value={form.senha} onChange={e => setForm({...form, senha: e.target.value})} required /></div>
            <div><Label>Confirmacao</Label><Input type="password" value={form.confirmacaoSenha} onChange={e => setForm({...form, confirmacaoSenha: e.target.value})} required /></div>
            <Button type="submit">Salvar</Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
