import { randomUUID } from "node:crypto";
import { requireIdentity } from "../../../../cursor/identity";
import { sql } from "../../../lib/db";
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
  const telefone = asString(body.telefone, 40);
  const endereco = asString(body.endereco, 200);
  const servico = asString(body.servico, 80);
  const urgencia = asUrgencia(body.urgencia);
  const descricao = asString(body.descricao, 4000);
  const transcricao = asString(body.transcricao, 4000);

  if (!descricao && !transcricao && !cliente) {
    return Response.json(
      { error: "Informe ao menos cliente ou descrição" },
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
      id, cliente, telefone, endereco, servico, urgencia, descricao, transcricao,
      status, criado_por, criado_por_nome
    ) values ($1,$2,$3,$4,$5,$6,$7,$8,'aguardando_nota',$9,$10)`,
    [
      id,
      cliente,
      telefone,
      endereco,
      servico || "Outro",
      urgencia,
      descricao || transcricao,
      transcricao,
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
