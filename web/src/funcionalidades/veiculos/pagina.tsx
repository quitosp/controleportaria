"use client";
import { useEffect, useState } from "react";
import { Card } from "@/compartilhados/componentes/ui/card";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { Label } from "@/compartilhados/componentes/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/compartilhados/componentes/ui/dialog";
import { api } from "@/compartilhados/servicos/api";
import { getSessao } from "@/compartilhados/servicos/auth";

export function PaginaVeiculos() {
  const sessao = getSessao();
  const [itens, setItens] = useState<any[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [novoOpen, setNovoOpen] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [form, setForm] = useState<Record<string, any>>({});

  async function carregar() {
    setCarregando(true);
    try {
      const r = await api.get("/api/Veiculo/v1/listar/1/100");
      setItens(r.data?.list ?? r.data?.List ?? []);
    } finally { setCarregando(false); }
  }

  useEffect(() => { carregar(); }, []);

  async function salvar(e: React.FormEvent) {
    e.preventDefault(); setErro(null);
    try {
      await api.post("/api/Veiculo/v1/salvar", { ...form, unidadeId: sessao?.unidadeId });
      setNovoOpen(false); setForm({});
      carregar();
    } catch (ex: any) {
      setErro(ex?.response?.data?.message ?? ex?.response?.data?.mensagem ?? "Falha ao salvar");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl">Veiculos</h1>
        <Button onClick={() => setNovoOpen(true)}>Nova Veiculo</Button>
      </div>
      {erro && <div className="text-sm text-destructive">{erro}</div>}

      <Card className="p-3">
        {carregando && <div>Carregando...</div>}
        {!carregando && itens.length === 0 && <div className="text-muted-foreground text-sm">Nenhum registro.</div>}
        <div className="space-y-2">
          {itens.map((it: any) => (
            <div key={it.id ?? it.veiculoId} className="p-2 hover:bg-muted rounded">
              <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(it, null, 2)}</pre>
            </div>
          ))}
        </div>
      </Card>

      <Dialog open={novoOpen} onOpenChange={setNovoOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Nova Veiculo</DialogTitle></DialogHeader>
          <form onSubmit={salvar} className="space-y-3">
            <div><Label>Placa</Label><Input type="text" value={form.placa ?? ""} onChange={e => setForm({ ...form, placa: e.target.value })} required /></div>
            <div><Label>Tipo (0=Cavalo, 1=Carreta, 2=CarretaSegunda)</Label><Input type="number" value={form.tipo ?? ""} onChange={e => setForm({ ...form, tipo: e.target.value })} required /></div>
            <div><Label>Transportadora ID (opcional)</Label><Input type="text" value={form.transportadoraId ?? ""} onChange={e => setForm({ ...form, transportadoraId: e.target.value })} /></div>
            <Button type="submit">Salvar</Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
