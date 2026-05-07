export const MotivoEntrada = { Carga: 0, Descarga: 1, Devolucao: 2, Outro: 3 } as const;
export const TipoCarga = { Frigorificada: 0, Seca: 1, Container: 2, Lavador: 3, Outro: 4 } as const;
export const DestinoPateo = { Interno: 0, Externo: 1, Lavador: 2 } as const;
export const EstadoMovimento = {
  NoPateoExterno: 0, ChamadoParaInterno: 1, NoPateoInterno: 2, NoLavador: 3,
  Saiu: 100, Cancelado: 200, Desistencia: 201,
} as const;
export const StatusMotorista = { Ativo: 0, Pendente: 1, Bloqueado: 2 } as const;
export const EstagioAnexo = { Chegada: 0, Entrada: 1, Saida: 2 } as const;

export function rotuloEstado(e: number): string {
  return ({
    0: "No patio externo",
    1: "Chamado para interno",
    2: "No patio interno",
    3: "No lavador",
    100: "Saiu",
    200: "Cancelado",
    201: "Desistencia",
  } as Record<number, string>)[e] ?? `Estado ${e}`;
}

export function rotuloMotivo(m: number): string {
  return ({ 0: "Carga", 1: "Descarga", 2: "Devolucao", 3: "Outro" } as Record<number, string>)[m] ?? "?";
}

export function rotuloTipoCarga(t: number): string {
  return ({ 0: "Frigorificada", 1: "Seca", 2: "Container", 3: "Lavador", 4: "Outro" } as Record<number, string>)[t] ?? "?";
}

export function rotuloStatusMotorista(s: number): string {
  return ({ 0: "Ativo", 1: "Pendente", 2: "Bloqueado" } as Record<number, string>)[s] ?? "?";
}
