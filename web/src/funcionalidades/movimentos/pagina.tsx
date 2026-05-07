"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Card } from "@/compartilhados/componentes/ui/card";
import { Badge } from "@/compartilhados/componentes/ui/badge";
import { Skeleton } from "@/compartilhados/componentes/ui/skeleton";
import { api } from "@/compartilhados/servicos/api";
import { rotuloEstado, rotuloMotivo } from "@/compartilhados/servicos/enums";

export function PaginaMovimentos() {
  const [itens, setItens] = useState<any[]>([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    api.get("/api/movimentos/v1/listar/1/50")
      .then(r => setItens(r.data?.list ?? r.data?.List ?? []))
      .finally(() => setCarregando(false));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl">Movimentos</h1>
      {carregando && Array.from({length:5}).map((_,i)=><Skeleton key={i} className="h-14" />)}
      {!carregando && itens.length === 0 && <Card className="p-6 text-center text-muted-foreground">Nenhum movimento encontrado</Card>}
      <div className="space-y-2">
        {itens.map(i => (
          <Link key={i.movimentoPortariaId} href={`/movimentos/${i.movimentoPortariaId}`}>
            <Card className="p-3 hover:bg-muted cursor-pointer">
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-medium">Carreta {i.carretaId?.slice(0,8)}…</div>
                  <div className="text-xs text-muted-foreground">{new Date(i.dataChegada).toLocaleString("pt-BR")} • {rotuloMotivo(i.motivo)}</div>
                </div>
                <Badge>{rotuloEstado(i.estado)}</Badge>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
