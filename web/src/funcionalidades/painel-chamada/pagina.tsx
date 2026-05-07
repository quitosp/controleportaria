"use client";
import { useCallback, useEffect, useState } from "react";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Card } from "@/compartilhados/componentes/ui/card";
import { Badge } from "@/compartilhados/componentes/ui/badge";
import { Skeleton } from "@/compartilhados/componentes/ui/skeleton";
import { api } from "@/compartilhados/servicos/api";
import { useSignalR } from "@/compartilhados/servicos/signalr";
import { rotuloMotivo, rotuloTipoCarga, rotuloEstado } from "@/compartilhados/servicos/enums";

type Item = {
  movimentoPortariaId: string;
  portariaChegadaId: string;
  carretaId: string;
  transportadoraId?: string;
  motoristaId: string;
  motivo: number;
  tipoCarga: number;
  produto?: string;
  setor?: string;
  dataChegada: string;
  minutosEspera: number;
  chamadaExpirada: boolean;
  estado: number;
};

export function PaginaPainelChamada() {
  const [itens, setItens] = useState<Item[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [acaoEm, setAcaoEm] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const carregar = useCallback(async () => {
    try {
      const { data } = await api.get<Item[]>("/api/painel-chamada/v1/listar");
      setItens(data);
    } catch {
      setErro("Falha ao carregar painel");
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => { carregar(); }, [carregar]);

  // SignalR atualiza ao receber qualquer evento
  const { conectado } = useSignalR(useCallback(() => { carregar(); }, [carregar]));

  async function chamar(id: string) {
    setAcaoEm(id);
    setErro(null);
    try {
      await api.post(`/api/movimentos/v1/${id}/chamar`);
      await carregar();
    } catch (ex: any) {
      setErro(ex?.response?.data?.Mensagem || "Falha ao chamar (talvez outro lider tenha chamado primeiro)");
    } finally {
      setAcaoEm(null);
    }
  }

  async function recancelar(id: string) {
    setAcaoEm(id);
    try {
      await api.post(`/api/movimentos/v1/${id}/recancelar-chamada`);
      await carregar();
    } finally {
      setAcaoEm(null);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl">Painel de chamada — Patio externo</h1>
          <div className="text-xs text-muted-foreground mt-1">
            Tempo real: <span className={conectado ? "text-success" : "text-destructive"}>{conectado ? "conectado" : "perdido — atualizando manualmente"}</span>
          </div>
        </div>
        <Button variant="outline" onClick={carregar}>Atualizar</Button>
      </div>

      {erro && <div className="text-sm text-destructive">{erro}</div>}

      {carregando && Array.from({length:3}).map((_,i)=><Skeleton key={i} className="h-20" />)}

      {!carregando && itens.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">Nenhum veiculo aguardando no patio externo</Card>
      )}

      <div className="space-y-3">
        {itens.map(i => (
          <Card key={i.movimentoPortariaId} className="p-4 flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-medium">Carreta: {i.carretaId.slice(0,8)}…</span>
                <Badge variant="secondary">{rotuloMotivo(i.motivo)}</Badge>
                <Badge variant="outline">{rotuloTipoCarga(i.tipoCarga)}</Badge>
                <Badge>{rotuloEstado(i.estado)}</Badge>
                {i.chamadaExpirada && <Badge variant="destructive">Chamada expirada</Badge>}
              </div>
              <div className="text-sm text-muted-foreground">
                {i.produto ?? "—"} • Setor {i.setor ?? "—"} • Espera {i.minutosEspera}min
              </div>
            </div>
            <div className="flex gap-2">
              {i.estado === 0 && (
                <Button onClick={() => chamar(i.movimentoPortariaId)} disabled={acaoEm === i.movimentoPortariaId}>
                  Autorizar entrada
                </Button>
              )}
              {i.estado === 1 && i.chamadaExpirada && (
                <Button variant="outline" onClick={() => recancelar(i.movimentoPortariaId)} disabled={acaoEm === i.movimentoPortariaId}>
                  Recancelar
                </Button>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
