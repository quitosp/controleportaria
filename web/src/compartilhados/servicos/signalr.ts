import { useEffect, useRef, useState } from "react";
import * as signalR from "@microsoft/signalr";
import { getToken, getSessao } from "./auth";

const baseURL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5270";

export function useSignalR(onEvent: (payload: string) => void) {
  const [conectado, setConectado] = useState(false);
  const ref = useRef<signalR.HubConnection | null>(null);

  useEffect(() => {
    const sessao = getSessao();
    if (!sessao?.unidadeId) return;

    const conn = new signalR.HubConnectionBuilder()
      .withUrl(`${baseURL}/hubs/painel-chamada`, {
        accessTokenFactory: () => getToken() ?? "",
      })
      .withAutomaticReconnect([0, 2000, 5000, 10000, 30000])
      .build();

    conn.on("evento", (payload: string) => onEvent(payload));
    conn.onreconnected(() => {
      setConectado(true);
      conn.invoke("EntrarGrupoUnidade", sessao.unidadeId).catch(() => {});
    });
    conn.onreconnecting(() => setConectado(false));
    conn.onclose(() => setConectado(false));

    conn
      .start()
      .then(() => {
        setConectado(true);
        return conn.invoke("EntrarGrupoUnidade", sessao.unidadeId);
      })
      .catch((e) => console.warn("SignalR start falhou", e));

    ref.current = conn;
    return () => {
      conn.stop().catch(() => {});
    };
  }, [onEvent]);

  return { conectado };
}
