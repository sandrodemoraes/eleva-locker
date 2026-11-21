export type Urgencia = "baixa" | "normal" | "alta";
export type ChamadoStatus =
  | "aberto"
  | "em_andamento"
  | "aguardando_nota"
  | "nota_feita"
  | "concluido"
  | "cancelado";

export const STATUS_LABEL: Record<ChamadoStatus, string> = {
  aberto: "Em aberto",
  em_andamento: "Em andamento",
  aguardando_nota: "Aguardando nota",
  nota_feita: "Nota feita",
  concluido: "Concluído",
  cancelado: "Cancelado",
};

export type Chamado = {
  id: string;
  cliente: string;
  quem_chamou: string;
  telefone: string;
  endereco: string;
  servico: string;
  urgencia: Urgencia;
  descricao: string;
  transcricao: string;
  audio_base64?: string;
  funcionarios: string;
  horario: string;
  marcado: boolean;
  status: ChamadoStatus;
  assumido_por?: string;
  assumido_em?: string | null;
  criado_por: string;
  criado_por_nome: string;
  criado_em: string;
  atualizado_em: string;
};

export type ChamadoInput = {
  cliente: string;
  quem_chamou: string;
  telefone: string;
  endereco: string;
  servico: string;
  urgencia: Urgencia;
  descricao: string;
  transcricao: string;
  audio_base64: string;
  funcionarios: string;
  horario: string;
  marcado: boolean;
  aberto?: boolean;
};

export type ChamadoEdit = {
  cliente?: string;
  quem_chamou?: string;
  telefone?: string;
  endereco?: string;
  servico?: string;
  urgencia?: Urgencia;
  descricao?: string;
  transcricao?: string;
  funcionarios?: string;
  horario?: string;
  marcado?: boolean;
  status?: ChamadoStatus;
};

export const SERVICOS = [
  "Câmeras",
  "Alarme",
  "Elétrica",
  "Energia solar",
  "Projeto",
  "Manutenção",
  "Outro",
] as const;
