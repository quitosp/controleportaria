"use client";
import { useState } from "react";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { Card } from "@/compartilhados/componentes/ui/card";
import { api } from "@/compartilhados/servicos/api";
import { rotuloEstado, EstadoMovimento } from "@/compartilhados/servicos/enums";

export function PaginaConfirmarEntrada() {
  const [id, setId] = useState("");
  const [movimento, setMovimento] = useState<any>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  async function buscar(e: React.FormEvent) {
    e.preventDefault();
    setMovimento(null); setErro(null); setMsg(null);
    try {
      const { data } = await api.get(`/api/movimentos/v1/${id}`);
      const mov = data?.Data ?? data?.data ?? data;
      if (mov.estado !== EstadoMovimento.ChamadoParaInterno) {
        setErro(`Movimento esta em ${rotuloEstado(mov.estado)} — apenas ChamadoParaInterno pode ser confirmado.`);
      }
      setMovimento(mov);
    } catch {
      setErro("Movimento nao encontrado");
    }
  }

  async function confirmar() {
    if (!movimento) return;
    setErro(null); setMsg(null);
    try {
      await api.post(`/api/movimentos/v1/${movimento.movimentoPortariaId}/confirmar-entrada`);
      setMsg("Entrada confirmada");
      setMovimento(null); setId("");
    } catch (ex: any) {
      setErro(ex?.response?.data?.Mensagem ?? "Falha ao confirmar entrada");
    }
  }

  return (
    <div className="max-w-xl space-y-4">
      <h1 className="text-2xl">Confirmar entrada</h1>
      <form onSubmit={buscar} className="flex gap-2">
        <Input placeholder="ID do movimento" value={id} onChange={e => setId(e.target.value)} />
        <Button type="submit">Buscar</Button>
      </form>
      {erro && <div className="text-sm text-destructive">{erro}</div>}
      {msg && <div className="text-sm text-success">{msg}</div>}
      {movimento && (
        <Card className="p-4 space-y-2">
          <div>Estado: <b>{rotuloEstado(movimento.estado)}</b></div>
          <div className="text-sm text-muted-foreground">
            Carreta: {movimento.carretaId?.slice(0,8)}… • Lider: {movimento.liderQueAutorizouId?.slice(0,8) ?? "—"} • Chamada: {movimento.dataChamada ?? "—"}
          </div>
          {movimento.estado === EstadoMovimento.ChamadoParaInterno && (
            <Button onClick={confirmar}>Confirmar entrada</Button>
          )}
        </Card>
      )}
    </div>
  );
}
