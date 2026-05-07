"use client";
import { useEffect, useState } from "react";
import { Card } from "@/compartilhados/componentes/ui/card";
import { Badge } from "@/compartilhados/componentes/ui/badge";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { Label } from "@/compartilhados/componentes/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/compartilhados/componentes/ui/dialog";
import { api } from "@/compartilhados/servicos/api";
import { rotuloStatusMotorista, StatusMotorista } from "@/compartilhados/servicos/enums";
import { papelMaiorOuIgual, getSessao } from "@/compartilhados/servicos/auth";

export function PaginaMotoristas() {
  const [itens, setItens] = useState<any[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [novoOpen, setNovoOpen] = useState(false);
  const [statusOpen, setStatusOpen] = useState<any>(null);
  const [erro, setErro] = useState<string | null>(null);
  const sessao = getSessao();
  const podeBloquear = papelMaiorOuIgual(sessao?.papel, "Supervisor");

  // form novo
  const [nome, setNome] = useState(""); const [cpf, setCpf] = useState(""); const [whatsapp, setWhatsapp] = useState(""); const [email, setEmail] = useState("");

  // form status
  const [novoStatus, setNovoStatus] = useState<number>(StatusMotorista.Bloqueado);
  const [motivoStatus, setMotivoStatus] = useState("");

  async function carregar() {
    setCarregando(true);
    try {
      const r = await api.get("/api/Motorista/v1/listar/1/100");
      setItens(r.data?.list ?? r.data?.List ?? []);
    } finally { setCarregando(false); }
  }

  useEffect(() => { carregar(); }, []);

  async function salvarNovo(e: React.FormEvent) {
    e.preventDefault(); setErro(null);
    try {
      await api.post("/api/Motorista/v1/salvar", {
        nome, cpf: cpf.replace(/\D/g,""), whatsapp, email,
        status: 0, motivoStatus: null,
        unidadeId: sessao?.unidadeId,
      });
      setNovoOpen(false); setNome(""); setCpf(""); setWhatsapp(""); setEmail("");
      carregar();
    } catch (ex: any) {
      setErro(ex?.response?.data?.message ?? "Falha ao salvar");
    }
  }

  async function alterarStatus(e: React.FormEvent) {
    e.preventDefault();
    if (novoStatus === StatusMotorista.Bloqueado && !motivoStatus.trim()) { setErro("Motivo obrigatorio."); return; }
    try {
      await api.put(`/api/Motorista/v1/${statusOpen.id}/status`, { status: novoStatus, motivoStatus });
      setStatusOpen(null); setMotivoStatus("");
      carregar();
    } catch (ex: any) {
      setErro(ex?.response?.data?.message ?? "Falha ao alterar status");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl">Motoristas</h1>
        <Button onClick={() => setNovoOpen(true)}>Novo motorista</Button>
      </div>
      {erro && <div className="text-sm text-destructive">{erro}</div>}

      <Card className="p-3">
        {carregando && <div>Carregando...</div>}
        {!carregando && itens.length === 0 && <div className="text-muted-foreground text-sm">Nenhum motorista cadastrado.</div>}
        <div className="space-y-2">
          {itens.map(m => (
            <div key={m.motoristaId ?? m.id} className="flex justify-between items-center p-2 hover:bg-muted rounded">
              <div>
                <div className="font-medium">{m.nome}</div>
                <div className="text-xs text-muted-foreground">CPF {m.cpf} • WA {m.whatsapp}</div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={m.status === StatusMotorista.Bloqueado ? "destructive" : m.status === StatusMotorista.Pendente ? "secondary" : "default"}>
                  {rotuloStatusMotorista(m.status)}
                </Badge>
                {podeBloquear && (
                  <Button variant="outline" size="sm" onClick={() => { setStatusOpen({ id: m.motoristaId ?? m.id, status: m.status }); setNovoStatus(m.status === 2 ? 0 : 2); setMotivoStatus(""); }}>
                    Alterar status
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Dialog open={novoOpen} onOpenChange={setNovoOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Novo motorista</DialogTitle></DialogHeader>
          <form onSubmit={salvarNovo} className="space-y-3">
            <div><Label>Nome</Label><Input value={nome} onChange={e=>setNome(e.target.value)} required /></div>
            <div><Label>CPF</Label><Input value={cpf} onChange={e=>setCpf(e.target.value)} required /></div>
            <div><Label>Whatsapp (E.164 ex: +5538999999999)</Label><Input value={whatsapp} onChange={e=>setWhatsapp(e.target.value)} required /></div>
            <div><Label>Email (opcional)</Label><Input type="email" value={email} onChange={e=>setEmail(e.target.value)} /></div>
            <Button type="submit">Salvar</Button>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={!!statusOpen} onOpenChange={() => setStatusOpen(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Alterar status</DialogTitle></DialogHeader>
          <form onSubmit={alterarStatus} className="space-y-3">
            <div>
              <Label>Status</Label>
              <select className="w-full rounded-md border bg-background p-2 text-sm" value={novoStatus} onChange={e => setNovoStatus(Number(e.target.value))}>
                <option value={0}>Ativo</option>
                <option value={1}>Pendente</option>
                <option value={2}>Bloqueado</option>
              </select>
            </div>
            <div>
              <Label>Motivo {novoStatus === 2 && <span className="text-destructive">*</span>}</Label>
              <Input value={motivoStatus} onChange={e => setMotivoStatus(e.target.value)} required={novoStatus === 2} />
            </div>
            <Button type="submit">Confirmar</Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
