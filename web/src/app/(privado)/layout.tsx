"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { AlternarTema } from "@/compartilhados/componentes/tema/alternar-tema";
import { Button } from "@/compartilhados/componentes/ui/button";
import { cn } from "@/compartilhados/lib/cn";
import { getSessao, sair, papelMaiorOuIgual } from "@/compartilhados/servicos/auth";
import { Home, Truck, BellRing, DoorOpen, DoorClosed, ListChecks, Users, Building2, UserCog, Factory } from "lucide-react";

const grupos = [
  { titulo: "Operacao", itens: [
    { rotulo: "Inicio", rota: "/dashboard", icone: Home },
    { rotulo: "Cadastrar chegada", rota: "/chegada", icone: Truck },
    { rotulo: "Painel de chamada", rota: "/painel-chamada", icone: BellRing },
    { rotulo: "Confirmar entrada", rota: "/confirmar-entrada", icone: DoorOpen },
    { rotulo: "Registrar saida", rota: "/saida", icone: DoorClosed },
    { rotulo: "Movimentos", rota: "/movimentos", icone: ListChecks },
  ]},
  { titulo: "Cadastros", itens: [
    { rotulo: "Motoristas", rota: "/motoristas", icone: Users },
    { rotulo: "Transportadoras", rota: "/transportadoras", icone: Building2 },
    { rotulo: "Veiculos", rota: "/veiculos", icone: Truck },
  ]},
  { titulo: "Administracao", itens: [
    { rotulo: "Usuarios", rota: "/usuarios", icone: UserCog },
    { rotulo: "Portarias", rota: "/portarias", icone: DoorClosed },
    { rotulo: "Unidades", rota: "/unidades", icone: Factory },
  ]},
];

export default function LayoutPrivado({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const router = useRouter();
  const [pronto, setPronto] = useState(false);
  const [sessao, setSessao] = useState<ReturnType<typeof getSessao>>(null);

  useEffect(() => {
    const s = getSessao();
    if (!s) {
      router.replace("/login");
      return;
    }
    setSessao(s);
    setPronto(true);
  }, [router]);

  if (!pronto) return null;

  // Filtro por papel
  const filtrarItens = (grupoTitulo: string) => {
    if (grupoTitulo === "Administracao") return papelMaiorOuIgual(sessao?.papel, "Admin");
    return true;
  };

  return (
    <div className="flex min-h-screen">
      <aside className="w-60 border-r bg-card">
        <div className="px-4 py-3 font-semibold text-lg">Portaria</div>
        <nav className="px-2 space-y-4">
          {grupos.filter(g => filtrarItens(g.titulo)).map(g => (
            <div key={g.titulo}>
              <div className="px-2 text-xs font-medium uppercase text-muted-foreground">{g.titulo}</div>
              <ul className="mt-1 space-y-0.5">
                {g.itens.map(i => {
                  const Icone = i.icone;
                  const ativo = path === i.rota;
                  return (
                    <li key={i.rota}>
                      <Link href={i.rota} className={cn(
                        "flex items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-muted",
                        ativo && "bg-muted text-foreground font-medium"
                      )}>
                        <Icone className="h-4 w-4" /> {i.rotulo}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>
      </aside>
      <main className="flex-1 flex flex-col">
        <header className="border-b px-4 py-2 flex justify-end items-center gap-3">
          <span className="text-sm text-muted-foreground">{sessao?.name} · {sessao?.papel}</span>
          <AlternarTema />
          <Button variant="outline" size="sm" onClick={sair}>Sair</Button>
        </header>
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
