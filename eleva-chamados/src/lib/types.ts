export type Urgencia = "baixa" | "normal" | "alta";
export type ChamadoStatus =
  | "aguardando_nota"
  | "nota_feita"
  | "concluido"
  | "cancelado";

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
