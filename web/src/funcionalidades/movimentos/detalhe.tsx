"use client";
import { useEffect, useState } from "react";
import { Card } from "@/compartilhados/componentes/ui/card";
import { Badge } from "@/compartilhados/componentes/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/compartilhados/componentes/ui/tabs";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { api } from "@/compartilhados/servicos/api";
import { rotuloEstado, rotuloMotivo, rotuloTipoCarga, EstagioAnexo } from "@/compartilhados/servicos/enums";
import { papelMaiorOuIgual, getSessao } from "@/compartilhados/servicos/auth";

export function DetalheMovimento({ id }: { id: string }) {
  const [mov, setMov] = useState<any>(null);
  const [eventos, setEventos] = useState<any[]>([]);
  const [anexos, setAnexos] = useState<any[]>([]);
  const [observacao, setObservacao] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const sessao = getSessao();
  const podeAuditoria = papelMaiorOuIgual(sessao?.papel, "Supervisor");

  async function carregar() {
    try {
      const r = await api.get(`/api/movimentos/v1/listar/1/1`); // workaround: lista filtra por nada — usuario passa por lista
      // melhor: dado diretamente do listar — mas para detalhe completo usamos endpoint dedicado se existir
    } catch {}
    try {
      const r = await api.get(`/api/movimentos/v1/${id}/anexos`);
      setAnexos(r.data ?? []);
    } catch {}
    if (podeAuditoria) {
      try {
        const r = await api.get(`/api/movimentos/v1/${id}/eventos`);
        setEventos(r.data ?? []);
      } catch {}
    }
    // Buscar movimento direto: usar listar + filter por id ou expor endpoint /api/movimentos/v1/{id}
    try {
      const r = await api.get(`/api/movimentos/v1/listar/1/1000`);
      const lista = r.data?.list ?? r.data?.List ?? [];
      setMov(lista.find((m: any) => m.movimentoPortariaId === id) ?? null);
    } catch {}
  }

  useEffect(() => { carregar(); }, [id]);

  async function cancelar() {
    if (!observacao.trim()) { setErro("Observacao obrigatoria."); return; }
    try {
      await api.post(`/api/movimentos/v1/${id}/cancelar`, { observacao });
      setMsg("Cancelado"); setObservacao(""); carregar();
    } catch (ex: any) { setErro(ex?.response?.data?.message ?? "Falha"); }
  }

  async function desistir() {
    if (!observacao.trim()) { setErro("Observacao obrigatoria."); return; }
    try {
      await api.post(`/api/movimentos/v1/${id}/desistir`, { observacao });
      setMsg("Desistencia registrada"); setObservacao(""); carregar();
    } catch (ex: any) { setErro(ex?.response?.data?.message ?? "Falha"); }
  }

  async function anexar(estagio: number, file: File) {
    const fd = new FormData();
    fd.append("arquivo", file);
    fd.append("estagio", estagio.toString());
    try {
      await api.post(`/api/movimentos/v1/${id}/anexar`, fd);
      carregar();
    } catch (ex: any) { setErro(ex?.response?.data?.message ?? "Falha no upload"); }
  }

  if (!mov) return <div className="p-4">Carregando...</div>;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl">Movimento {id.slice(0,8)}…</h1>
          <div className="text-sm text-muted-foreground">{rotuloMotivo(mov.motivo)} • {rotuloTipoCarga(mov.tipoCarga)} • Carreta {mov.carretaId?.slice(0,8)}…</div>
        </div>
        <Badge>{rotuloEstado(mov.estado)}</Badge>
      </div>

      {erro && <div className="text-sm text-destructive">{erro}</div>}
      {msg && <div className="text-sm text-success">{msg}</div>}

      <Tabs defaultValue="dados">
        <TabsList>
          <TabsTrigger value="dados">Dados</TabsTrigger>
          <TabsTrigger value="anexos">Anexos</TabsTrigger>
          {podeAuditoria && <TabsTrigger value="auditoria">Auditoria</TabsTrigger>}
          <TabsTrigger value="acoes">Acoes</TabsTrigger>
        </TabsList>

        <TabsContent value="dados">
          <Card className="p-4 grid grid-cols-2 gap-3 text-sm">
            <div><b>Chegada:</b> {new Date(mov.dataChegada).toLocaleString("pt-BR")}</div>
            <div><b>Porteiro:</b> {mov.porteiroChegadaId?.slice(0,8)}…</div>
            <div><b>Motorista:</b> {mov.motoristaId?.slice(0,8)}…</div>
            <div><b>Transportadora:</b> {mov.transportadoraId?.slice(0,8) ?? "—"}…</div>
            <div><b>Lider chamou:</b> {mov.liderQueAutorizouId?.slice(0,8) ?? "—"}…</div>
            <div><b>Saida:</b> {mov.dataSaida ? new Date(mov.dataSaida).toLocaleString("pt-BR") : "—"}</div>
            <div><b>NF saida:</b> {mov.numeroNFSaida ?? "—"}</div>
            <div><b>Lacre:</b> {mov.lacre ?? "—"}</div>
            <div><b>Destino saida:</b> {mov.destinoSaida ?? "—"}</div>
            <div className="col-span-2"><b>Observacao:</b> {mov.observacao ?? "—"}</div>
          </Card>
        </TabsContent>

        <TabsContent value="anexos">
          <Card className="p-4 space-y-3">
            <div className="flex gap-2 items-end">
              <input type="file" accept="image/jpeg,image/png,application/pdf"
                onChange={e => e.target.files?.[0] && anexar(EstagioAnexo.Chegada, e.target.files[0])} />
              <span className="text-xs text-muted-foreground">(estagio Chegada)</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {anexos.map(a => (
                <div key={a.id} className="text-xs border p-2 rounded">
                  <div>{a.estagio === 0 ? "Chegada" : a.estagio === 1 ? "Entrada" : "Saida"} • {Math.round(a.tamanhoBytes/1024)}kB</div>
                  <a className="text-primary underline" href={a.url} target="_blank">Abrir</a>
                </div>
              ))}
              {anexos.length === 0 && <div className="text-sm text-muted-foreground">Nenhum anexo.</div>}
            </div>
          </Card>
        </TabsContent>

        {podeAuditoria && (
          <TabsContent value="auditoria">
            <Card className="p-4">
              <div className="space-y-2 text-sm">
                {eventos.map(e => (
                  <div key={e.id} className="border-l-2 border-primary pl-3">
                    <div className="font-medium">{e.tipo} {e.deEstado != null && `(${rotuloEstado(e.deEstado)} → ${rotuloEstado(e.paraEstado)})`}</div>
                    <div className="text-xs text-muted-foreground">{new Date(e.quando).toLocaleString("pt-BR")} • {e.usuarioId?.slice(0,8)}…</div>
                    {e.detalhes && <div className="text-xs mt-1">{e.detalhes}</div>}
                  </div>
                ))}
                {eventos.length === 0 && <div className="text-muted-foreground">Sem eventos</div>}
              </div>
            </Card>
          </TabsContent>
        )}

        <TabsContent value="acoes">
          <Card className="p-4 space-y-3">
            <div className="text-sm">Cancelar ou registrar desistencia (exige observacao):</div>
            <Input placeholder="Motivo (obrigatorio)" value={observacao} onChange={e => setObservacao(e.target.value)} />
            <div className="flex gap-2">
              <Button variant="destructive" onClick={cancelar}>Cancelar movimento</Button>
              <Button variant="outline" onClick={desistir}>Registrar desistencia</Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
