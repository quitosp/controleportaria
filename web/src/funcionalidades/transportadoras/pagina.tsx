"use client";
import { useEffect, useState } from "react";
import { Card } from "@/compartilhados/componentes/ui/card";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { Label } from "@/compartilhados/componentes/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/compartilhados/componentes/ui/dialog";
import { api } from "@/compartilhados/servicos/api";
import { getSessao } from "@/compartilhados/servicos/auth";

export function PaginaTransportadoras() {
  const sessao = getSessao();
  const [itens, setItens] = useState<any[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [novoOpen, setNovoOpen] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [form, setForm] = useState<Record<string, any>>({});

  async function carregar() {
    setCarregando(true);
    try {
      const r = await api.get("/api/Transportadora/v1/listar/1/100");
      setItens(r.data?.list ?? r.data?.List ?? []);
    } finally { setCarregando(false); }
  }

  useEffect(() => { carregar(); }, []);

  async function salvar(e: React.FormEvent) {
    e.preventDefault(); setErro(null);
    try {
      await api.post("/api/Transportadora/v1/salvar", { ...form, unidadeId: sessao?.unidadeId });
      setNovoOpen(false); setForm({});
      carregar();
    } catch (ex: any) {
      setErro(ex?.response?.data?.message ?? ex?.response?.data?.mensagem ?? "Falha ao salvar");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl">Transportadoras</h1>
        <Button onClick={() => setNovoOpen(true)}>Nova Transportadora</Button>
      </div>
      {erro && <div className="text-sm text-destructive">{erro}</div>}

      <Card className="p-3">
        {carregando && <div>Carregando...</div>}
        {!carregando && itens.length === 0 && <div className="text-muted-foreground text-sm">Nenhum registro.</div>}
        <div className="space-y-2">
          {itens.map((it: any) => (
            <div key={it.id ?? it.transportadoraId} className="p-2 hover:bg-muted rounded">
              <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(it, null, 2)}</pre>
            </div>
          ))}
        </div>
      </Card>

      <Dialog open={novoOpen} onOpenChange={setNovoOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Nova Transportadora</DialogTitle></DialogHeader>
          <form onSubmit={salvar} className="space-y-3">
            <div><Label>Razao social</Label><Input type="text" value={form.razaoSocial ?? ""} onChange={e => setForm({ ...form, razaoSocial: e.target.value })} required /></div>
            <div><Label>CNPJ</Label><Input type="text" value={form.cnpj ?? ""} onChange={e => setForm({ ...form, cnpj: e.target.value })} required /></div>
            <Button type="submit">Salvar</Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
