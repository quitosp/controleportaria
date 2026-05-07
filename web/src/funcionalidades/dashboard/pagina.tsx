"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Card } from "@/compartilhados/componentes/ui/card";
import { Skeleton } from "@/compartilhados/componentes/ui/skeleton";
import { Button } from "@/compartilhados/componentes/ui/button";
import { api } from "@/compartilhados/servicos/api";
import { getSessao, papelMaiorOuIgual } from "@/compartilhados/servicos/auth";

type ResumoDia = {
  noPateoExterno: number; noPateoInterno: number;
  saiuHoje: number; canceladosHoje: number; total: number;
};

export function PaginaDashboard() {
  const [resumo, setResumo] = useState<ResumoDia | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const sessao = getSessao();

  useEffect(() => {
    api.get<ResumoDia>("/api/movimentos/v1/resumo-dia")
      .then(r => setResumo(r.data))
      .catch(e => setErro("Falha ao carregar resumo"));
  }, []);

  const ehLider = papelMaiorOuIgual(sessao?.papel, "Lider");

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl">Inicio</h1>
        <div className="flex gap-2">
          {ehLider && <Link href="/painel-chamada"><Button variant="outline">Painel de chamada</Button></Link>}
          <Link href="/chegada"><Button>Nova chegada</Button></Link>
        </div>
      </div>
      {erro && <div className="text-destructive text-sm">{erro}</div>}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {!resumo && Array.from({length:4}).map((_,i)=> <Skeleton key={i} className="h-24" />)}
        {resumo && (
          <>
            <KPI titulo="No patio externo" valor={resumo.noPateoExterno} />
            <KPI titulo="No patio interno" valor={resumo.noPateoInterno} />
            <KPI titulo="Saiu hoje" valor={resumo.saiuHoje} />
            <KPI titulo="Cancelados hoje" valor={resumo.canceladosHoje} />
          </>
        )}
      </div>
    </div>
  );
}

function KPI({ titulo, valor }: { titulo: string; valor: number }) {
  return (
    <Card className="p-4">
      <div className="text-xs uppercase text-muted-foreground">{titulo}</div>
      <div className="text-3xl font-semibold mt-2">{valor}</div>
    </Card>
  );
}
