/** Nomes da equipe Eleva — ajuste aqui quando entrar alguém novo. */
export const EQUIPE = [
  "Sandro de Moraes",
  "Fabio Nuernberg",
  "Crhistian",
  "Ramalho",
  "Joares",
  "Kassandra Oliveira Coelho",
] as const;

export function parseFuncionarios(value: string): string[] {
  return value
    .split(/[,;/|]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function joinFuncionarios(names: string[]): string {
  return [...new Set(names.map((n) => n.trim()).filter(Boolean))].join(", ");
}
