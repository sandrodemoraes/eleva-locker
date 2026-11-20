export type Urgencia = "baixa" | "normal" | "alta";
export type ChamadoStatus =
  | "aguardando_nota"
  | "nota_feita"
  | "concluido"
  | "cancelado";

export type Chamado = {
  id: string;
  cliente: string;
  telefone: string;
  endereco: string;
  servico: string;
  urgencia: Urgencia;
  descricao: string;
  transcricao: string;
  audio_base64?: string;
  status: ChamadoStatus;
  criado_por: string;
  criado_por_nome: string;
  criado_em: string;
  atualizado_em: string;
};

export type ChamadoInput = {
  cliente: string;
  telefone: string;
  endereco: string;
  servico: string;
  urgencia: Urgencia;
  descricao: string;
  transcricao: string;
  audio_base64: string;
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
