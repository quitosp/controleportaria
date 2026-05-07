"use client";
import { useState } from "react";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { Label } from "@/compartilhados/componentes/ui/label";
import { Card } from "@/compartilhados/componentes/ui/card";
import { api } from "@/compartilhados/servicos/api";
import { rotuloEstado, rotuloMotivo, MotivoEntrada, TipoCarga } from "@/compartilhados/servicos/enums";

export function PaginaSaida() {
  const [id, setId] = useState("");
  const [mov, setMov] = useState<any>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [numeroNF, setNF] = useState("");
  const [lacre, setLacre] = useState("");
  const [destino, setDestino] = useState("");
  const [container, setContainer] = useState("");
  const [contrato, setContrato] = useState("");

  async function buscar(e: React.FormEvent) {
    e.preventDefault();
    setMov(null); setErro(null); setMsg(null);
    try {
      const { data } = await api.get(`/api/movimentos/v1/${id}`);
      const m = data?.Data ?? data?.data ?? data;
      setMov(m);
    } catch {
      setErro("Movimento nao encontrado");
    }
  }

  const ehCarga = mov?.motivo === MotivoEntrada.Carga;
  const ehContainer = ehCarga && mov?.tipoCarga === TipoCarga.Container;

  async function registrar() {
    if (!mov) return;
    setErro(null); setMsg(null);
    try {
      const payload = ehCarga
        ? { numeroNF, lacre, destino, numeroContainer: ehContainer ? container : null, contrato: ehContainer ? contrato : null }
        : {};
      await api.post(`/api/movimentos/v1/${mov.movimentoPortariaId}/registrar-saida`, payload);
      setMsg("Saida registrada");
      setMov(null); setId(""); setNF(""); setLacre(""); setDestino(""); setContainer(""); setContrato("");
    } catch (ex: any) {
      setErro(ex?.response?.data?.message ?? "Falha ao registrar saida (campos faltantes?)");
    }
  }

  return (
    <div className="max-w-xl space-y-4">
      <h1 className="text-2xl">Registrar saida</h1>
      <form onSubmit={buscar} className="flex gap-2">
        <Input placeholder="ID do movimento" value={id} onChange={e => setId(e.target.value)} />
        <Button type="submit">Buscar</Button>
      </form>

      {erro && <div className="text-sm text-destructive">{erro}</div>}
      {msg && <div className="text-sm text-success">{msg}</div>}

      {mov && (
        <Card className="p-4 space-y-3">
          <div className="text-sm">
            Estado: <b>{rotuloEstado(mov.estado)}</b> • Motivo: <b>{rotuloMotivo(mov.motivo)}</b>
          </div>
          {ehCarga && (
            <>
              <div><Label>Numero NF</Label><Input value={numeroNF} onChange={e=>setNF(e.target.value)} required /></div>
              <div><Label>Lacre</Label><Input value={lacre} onChange={e=>setLacre(e.target.value)} required /></div>
              <div><Label>Destino</Label><Input value={destino} onChange={e=>setDestino(e.target.value)} required /></div>
              {ehContainer && (
                <>
                  <div><Label>Numero Container</Label><Input value={container} onChange={e=>setContainer(e.target.value)} required /></div>
                  <div><Label>Contrato</Label><Input value={contrato} onChange={e=>setContrato(e.target.value)} required /></div>
                </>
              )}
            </>
          )}
          {!ehCarga && <div className="text-sm text-muted-foreground">Saida de Descarga: apenas confirmar.</div>}
          <Button onClick={registrar}>Registrar saida</Button>
        </Card>
      )}
    </div>
  );
}
