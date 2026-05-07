"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { Label } from "@/compartilhados/componentes/ui/label";
import { Card } from "@/compartilhados/componentes/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/compartilhados/componentes/ui/dialog";
import { api } from "@/compartilhados/servicos/api";
import { MotivoEntrada, TipoCarga, DestinoPateo, StatusMotorista } from "@/compartilhados/servicos/enums";
import { getSessao } from "@/compartilhados/servicos/auth";

interface AutoFill { transportadoraId?: string; tipoCargaSugerida?: number; temHistorico?: boolean; }
interface Motorista { id: string; nome: string; cpf: string; whatsapp: string; status: number; motivoStatus?: string; }

export function PaginaChegada() {
  const router = useRouter();
  const sessao = getSessao();
  const [carretaId, setCarretaId] = useState("");
  const [cavaloId, setCavaloId] = useState("");
  const [motoristaId, setMotoristaId] = useState("");
  const [motoristaSel, setMotoristaSel] = useState<Motorista | null>(null);
  const [transportadoraId, setTransportadoraId] = useState("");
  const [motivo, setMotivo] = useState<number>(MotivoEntrada.Carga);
  const [tipoCarga, setTipoCarga] = useState<number>(TipoCarga.Frigorificada);
  const [destino, setDestino] = useState<number>(DestinoPateo.Externo);
  const [autorizadoPor, setAutorizadoPor] = useState("");
  const [numeroNF, setNumeroNF] = useState("");
  const [produto, setProduto] = useState("");
  const [setor, setSetor] = useState("");
  const [observacao, setObservacao] = useState("");
  const [autoFill, setAutoFill] = useState<AutoFill | null>(null);
  const [alertaBloqueio, setAlertaBloqueio] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function buscarAutoFill() {
    if (!carretaId) return;
    try {
      const { data } = await api.get<AutoFill>(`/api/movimentos/v1/buscar-por-placa/${carretaId}/auto-fill`);
      if (data?.temHistorico) setAutoFill(data);
    } catch {}
  }

  function aplicarAutoFill() {
    if (!autoFill) return;
    if (autoFill.transportadoraId) setTransportadoraId(autoFill.transportadoraId);
    if (typeof autoFill.tipoCargaSugerida === "number") setTipoCarga(autoFill.tipoCargaSugerida);
    setAutoFill(null);
  }

  async function buscarMotorista(id: string) {
    if (!id) return;
    try {
      const { data } = await api.get<Motorista>(`/api/Motorista/v1/${id}`);
      setMotoristaSel(data);
      if (data?.status === StatusMotorista.Bloqueado) setAlertaBloqueio(true);
    } catch {
      setMotoristaSel(null);
    }
  }

  async function submeter(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    if (motoristaSel?.status === StatusMotorista.Bloqueado && !observacao.trim()) {
      setAlertaBloqueio(true);
      setErro("Motorista bloqueado: observacao obrigatoria.");
      return;
    }
    setEnviando(true);
    try {
      const payload = {
        portariaChegadaId: sessao?.portariaPadraoId,
        motoristaId, carretaId, cavaloId: cavaloId || null,
        transportadoraId: transportadoraId || null,
        motivo, tipoCarga, destino,
        autorizadoPorChegada: destino === DestinoPateo.Interno ? autorizadoPor : null,
        numeroNFChegada: numeroNF || null,
        produto: produto || null,
        setor: setor || null,
        observacao: observacao || null,
      };
      const { data } = await api.post<any>("/api/movimentos/v1/cadastrar-chegada", payload);
      const sucesso = data?.success ?? data?.Success;
      if (!sucesso) {
        setErro(data?.message ?? data?.Message ?? "Falha ao cadastrar chegada");
        return;
      }
      const id = data?.data?.id ?? data?.data?.id;
      router.push(id ? `/movimentos/${id}` : "/movimentos");
    } catch (ex: any) {
      setErro(ex?.response?.data?.message ?? "Falha ao cadastrar chegada");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="max-w-3xl space-y-4">
      <h1 className="text-2xl">Cadastrar chegada</h1>
      {autoFill && (
        <Card className="p-3 bg-warning/10 border-warning">
          <div className="text-sm">
            Sugerimos transportadora <b>{autoFill.transportadoraId?.slice(0,8)}…</b> e tipo de carga do ultimo movimento desta placa.
            <Button size="sm" className="ml-3" onClick={aplicarAutoFill}>Aceitar</Button>
            <Button size="sm" variant="outline" className="ml-2" onClick={() => setAutoFill(null)}>Editar</Button>
          </div>
        </Card>
      )}
      <form onSubmit={submeter} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Campo label="Carreta (ID veiculo)" value={carretaId} onChange={setCarretaId} onBlur={buscarAutoFill} required />
        <Campo label="Cavalo (ID veiculo, opcional)" value={cavaloId} onChange={setCavaloId} />
        <Campo label="Motorista (ID)" value={motoristaId} onChange={setMotoristaId} onBlur={() => buscarMotorista(motoristaId)} required />
        <Campo label="Transportadora (ID, opcional)" value={transportadoraId} onChange={setTransportadoraId} />

        <Selecao label="Motivo" value={motivo} onChange={setMotivo} opcoes={[
          [MotivoEntrada.Carga,"Carga"],[MotivoEntrada.Descarga,"Descarga"],[MotivoEntrada.Devolucao,"Devolucao"],[MotivoEntrada.Outro,"Outro"]
        ]} />
        <Selecao label="Tipo carga" value={tipoCarga} onChange={setTipoCarga} opcoes={[
          [TipoCarga.Frigorificada,"Frigorificada"],[TipoCarga.Seca,"Seca"],[TipoCarga.Container,"Container"],[TipoCarga.Lavador,"Lavador"],[TipoCarga.Outro,"Outro"]
        ]} />
        <Selecao label="Destino" value={destino} onChange={setDestino} opcoes={[
          [DestinoPateo.Externo,"Patio externo"],[DestinoPateo.Interno,"Patio interno"],[DestinoPateo.Lavador,"Lavador"]
        ]} />
        {destino === DestinoPateo.Interno && (
          <Campo label="Autorizado por (obrigatorio)" value={autorizadoPor} onChange={setAutorizadoPor} required />
        )}

        <Campo label="NF (opcional na chegada)" value={numeroNF} onChange={setNumeroNF} />
        <Campo label="Produto" value={produto} onChange={setProduto} />
        <Campo label="Setor" value={setor} onChange={setSetor} />

        <div className="md:col-span-2">
          <Label>Observacao</Label>
          <textarea className="w-full mt-2 rounded-md border bg-background p-2 text-sm" rows={3} value={observacao} onChange={e => setObservacao(e.target.value)} />
        </div>

        {erro && <div className="md:col-span-2 text-sm text-destructive">{erro}</div>}

        <div className="md:col-span-2 flex gap-2">
          <Button type="submit" disabled={enviando}>{enviando ? "Salvando..." : "Salvar chegada"}</Button>
        </div>
      </form>

      <Dialog open={alertaBloqueio} onOpenChange={setAlertaBloqueio}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-destructive">Motorista bloqueado</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <p className="text-sm">Motivo: <b>{motoristaSel?.motivoStatus ?? "nao informado"}</b></p>
            <p className="text-sm text-muted-foreground">Para prosseguir, informe a observacao no formulario explicando a decisao. Esta acao sera registrada na auditoria.</p>
            <Button onClick={() => setAlertaBloqueio(false)}>Entendi</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function Campo({ label, value, onChange, onBlur, required }: { label: string; value: string; onChange: (v:string)=>void; onBlur?: ()=>void; required?: boolean }) {
  return (
    <div className="space-y-1">
      <Label>{label}</Label>
      <Input value={value} onChange={e => onChange(e.target.value)} onBlur={onBlur} required={required} />
    </div>
  );
}

function Selecao<T extends number>({ label, value, onChange, opcoes }: { label: string; value: T; onChange: (v:T)=>void; opcoes: [T,string][] }) {
  return (
    <div className="space-y-1">
      <Label>{label}</Label>
      <select className="w-full rounded-md border bg-background p-2 text-sm" value={value} onChange={e => onChange(Number(e.target.value) as T)}>
        {opcoes.map(([v,r]) => <option key={v} value={v}>{r}</option>)}
      </select>
    </div>
  );
}
