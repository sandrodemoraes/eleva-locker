import type { ChamadoInput, Urgencia } from "./types";
import { SERVICOS } from "./types";

const SERVICO_ALIASES: { label: (typeof SERVICOS)[number]; terms: string[] }[] =
  [
    {
      label: "Câmeras",
      terms: ["camera", "câmera", "cameras", "câmeras", "cftv", "monitoramento"],
    },
    {
      label: "Alarme",
      terms: ["alarme", "cerca eletrica", "cerca elétrica", "sensor"],
    },
    {
      label: "Elétrica",
      terms: ["eletrica", "elétrica", "eletricista", "quadro", "disjuntor"],
    },
    {
      label: "Energia solar",
      terms: ["solar", "painel", "fotovolta", "inversor"],
    },
    { label: "Projeto", terms: ["projeto", "laudo", "planta"] },
    {
      label: "Manutenção",
      terms: ["manutencao", "manutenção", "reparo", "conserto", "visita tecnica", "visita técnica"],
    },
  ];

function pickServico(text: string): string {
  const lower = text.toLowerCase();
  for (const entry of SERVICO_ALIASES) {
    if (entry.terms.some((t) => lower.includes(t))) return entry.label;
  }
  return "Outro";
}

function pickUrgencia(text: string): Urgencia {
  const lower = text.toLowerCase();
  if (
    /urg[eê]n|prioridade alta|hoje mesmo|emerg[eê]ncia|o quanto antes|asap/.test(
      lower,
    )
  ) {
    return "alta";
  }
  if (/sem pressa|quando puder|baixa prioridade/.test(lower)) return "baixa";
  return "normal";
}

function captureAfter(
  text: string,
  labels: string[],
  stopLabels: string[],
): string {
  const lower = text.toLowerCase();
  for (const label of labels) {
    const idx = lower.indexOf(label);
    if (idx === -1) continue;
    let rest = text.slice(idx + label.length).replace(/^[\s:,-]+/, "");
    let cut = rest.length;
    const restLower = rest.toLowerCase();
    for (const stop of stopLabels) {
      const s = restLower.indexOf(stop);
      if (s !== -1 && s < cut) cut = s;
    }
    rest = rest.slice(0, cut).replace(/[.,;]\s*$/, "").trim();
    if (rest) return rest;
  }
  return "";
}

/** Extrai campos estruturados de uma fala em português. */
export function parseChamadoFromSpeech(transcricao: string): ChamadoInput {
  const text = transcricao.trim().replace(/\s+/g, " ");
  const stop = [
    "cliente",
    "telefone",
    "fone",
    "whatsapp",
    "endereço",
    "endereco",
    "serviço",
    "servico",
    "instalação",
    "instalacao",
    "manutenção",
    "manutencao",
    "urgência",
    "urgencia",
    "observação",
    "observacao",
    "obs",
    "camera",
    "câmera",
    "alarme",
    "elétrica",
    "eletrica",
    "solar",
  ];

  const cliente =
    captureAfter(
      text,
      ["cliente ", "cliente:", "para o cliente ", "do cliente ", "dona ", "dono "],
      stop.filter((s) => !s.startsWith("cliente")),
    ) || "";

  const telefone =
    captureAfter(
      text,
      ["telefone ", "telefone:", "fone ", "whatsapp ", "celular "],
      stop.filter((s) => !["telefone", "fone", "whatsapp"].includes(s)),
    ) ||
    (text.match(
      /(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\s?)?\d{4}[-\s]?\d{4}/,
    )?.[0] ?? "");

  const endereco =
    captureAfter(
      text,
      ["endereço ", "endereco ", "endereço:", "endereco:", "na rua ", "no bairro ", "em "],
      stop.filter((s) => !s.includes("endere")),
    ) || "";

  const descricao = text;
  const servico = pickServico(text);
  const urgencia = pickUrgencia(text);

  return {
    cliente: cliente.slice(0, 120),
    telefone: telefone.slice(0, 40),
    endereco: endereco.slice(0, 200),
    servico,
    urgencia,
    descricao,
    transcricao: text,
    audio_base64: "",
  };
}

export function textoParaNota(c: {
  cliente: string;
  telefone: string;
  endereco: string;
  servico: string;
  urgencia: string;
  descricao: string;
}): string {
  return [
    `Cliente: ${c.cliente || "—"}`,
    `Telefone: ${c.telefone || "—"}`,
    `Endereço: ${c.endereco || "—"}`,
    `Serviço: ${c.servico || "—"}`,
    `Urgência: ${c.urgencia || "—"}`,
    `Detalhes: ${c.descricao || "—"}`,
  ].join("\n");
}
