import { randomUUID } from "node:crypto";
import { requireIdentity } from "../../../../cursor/identity";
import { sql } from "../../../lib/db";
import { transcribeAudioDataUrl } from "../../../lib/transcribe";
import type { Chamado, ChamadoInput, Urgencia } from "../../../lib/types";

export const dynamic = "force-dynamic";

function asString(value: unknown, max = 2000): string {
  if (typeof value !== "string") return "";
  return value.trim().slice(0, max);
}

function asUrgencia(value: unknown): Urgencia {
  if (value === "baixa" || value === "alta" || value === "normal") return value;
  return "normal";
}

export async function GET(request: Request) {
  const identity = await requireIdentity(request);
  if (identity instanceof Response) return identity;

  const url = new URL(request.url);
  const status = url.searchParams.get("status");

  let rows: Chamado[];
  if (status) {
    rows = await sql<Chamado>(
      `select * from chamados where status = $1 order by criado_em desc limit 200`,
      [status],
    );
  } else {
    rows = await sql<Chamado>(
      `select * from chamados order by criado_em desc limit 200`,
    );
  }

  return Response.json(
    { chamados: rows },
    { headers: { "cache-control": "private, no-store" } },
  );
}

export async function POST(request: Request) {
  const identity = await requireIdentity(request);
  if (identity instanceof Response) return identity;

  let body: Partial<ChamadoInput>;
  try {
    body = (await request.json()) as Partial<ChamadoInput>;
  } catch {
    return Response.json({ error: "JSON inválido" }, { status: 400 });
  }

  const cliente = asString(body.cliente, 120);
  const quem_chamou = asString(body.quem_chamou, 120);
  const telefone = asString(body.telefone, 40);
  const endereco = asString(body.endereco, 200);
  const servico = asString(body.servico, 80);
  const urgencia = asUrgencia(body.urgencia);
  let descricao = asString(body.descricao, 4000);
  let transcricao = asString(body.transcricao, 4000);
  const audioRaw = asString(body.audio_base64, 900_000);
  const audio_base64 = audioRaw.startsWith("data:audio/") ? audioRaw : "";

  if (audio_base64 && !transcricao.trim()) {
    const whispered = await transcribeAudioDataUrl(audio_base64);
    if (whispered.text) {
      transcricao = whispered.text.slice(0, 4000);
      if (!descricao) descricao = transcricao;
    }
  }

  if (!descricao && !transcricao && !cliente && !audio_base64) {
    return Response.json(
      { error: "Informe áudio, cliente ou descrição" },
      { status: 400 },
    );
  }

  const id = randomUUID();
  const nome =
    ("name" in identity && typeof identity.name === "string" && identity.name) ||
    ("email" in identity && typeof identity.email === "string" && identity.email) ||
    "Equipe Eleva";

  await sql(
    `insert into chamados (
      id, cliente, quem_chamou, telefone, endereco, servico, urgencia, descricao, transcricao,
      audio_base64, status, criado_por, criado_por_nome
    ) values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,'aguardando_nota',$11,$12)`,
    [
      id,
      cliente,
      quem_chamou,
      telefone,
      endereco,
      servico || "Outro",
      urgencia,
      descricao || transcricao,
      transcricao,
      audio_base64,
      identity.sub,
      nome,
    ],
  );

  const [criado] = await sql<Chamado>(
    `select * from chamados where id = $1`,
    [id],
  );

  return Response.json(
    { chamado: criado },
    { status: 201, headers: { "cache-control": "private, no-store" } },
  );
}
