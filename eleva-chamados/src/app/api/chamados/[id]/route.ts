import { requireIdentity } from "../../../../../cursor/identity";
import { sql } from "../../../../lib/db";
import type {
  Chamado,
  ChamadoEdit,
  ChamadoStatus,
  Urgencia,
} from "../../../../lib/types";

export const dynamic = "force-dynamic";

const STATUSES: ChamadoStatus[] = [
  "aberto",
  "em_andamento",
  "aguardando_nota",
  "nota_feita",
  "concluido",
  "cancelado",
];

function asString(value: unknown, max: number): string | undefined {
  if (typeof value !== "string") return undefined;
  return value.trim().slice(0, max);
}

function asUrgencia(value: unknown): Urgencia | undefined {
  if (value === "baixa" || value === "alta" || value === "normal") return value;
  return undefined;
}

export async function PATCH(
  request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const identity = await requireIdentity(request);
  if (identity instanceof Response) return identity;

  const { id } = await context.params;
  if (!id || id.length > 80) {
    return Response.json({ error: "id inválido" }, { status: 400 });
  }

  let body: ChamadoEdit;
  try {
    body = (await request.json()) as ChamadoEdit;
  } catch {
    return Response.json({ error: "JSON inválido" }, { status: 400 });
  }

  const sets: string[] = [];
  const params: unknown[] = [];
  let i = 1;

  const add = (col: string, value: unknown) => {
    sets.push(`${col} = $${i}`);
    params.push(value);
    i += 1;
  };

  const cliente = asString(body.cliente, 120);
  if (cliente !== undefined) add("cliente", cliente);

  const quem = asString(body.quem_chamou, 120);
  if (quem !== undefined) add("quem_chamou", quem);

  const telefone = asString(body.telefone, 40);
  if (telefone !== undefined) add("telefone", telefone);

  const endereco = asString(body.endereco, 200);
  if (endereco !== undefined) add("endereco", endereco);

  const servico = asString(body.servico, 80);
  if (servico !== undefined) add("servico", servico || "Outro");

  const urgencia = asUrgencia(body.urgencia);
  if (urgencia !== undefined) add("urgencia", urgencia);

  const descricao = asString(body.descricao, 4000);
  if (descricao !== undefined) add("descricao", descricao);

  const transcricao = asString(body.transcricao, 4000);
  if (transcricao !== undefined) add("transcricao", transcricao);

  const funcionarios = asString(body.funcionarios, 300);
  if (funcionarios !== undefined) add("funcionarios", funcionarios);

  const horario = asString(body.horario, 80);
  if (horario !== undefined) add("horario", horario);

  if (typeof body.marcado === "boolean") add("marcado", body.marcado);

  if (body.status !== undefined) {
    if (!STATUSES.includes(body.status)) {
      return Response.json({ error: "status inválido" }, { status: 400 });
    }
    add("status", body.status);
  }

  if (sets.length === 0) {
    return Response.json({ error: "nada para atualizar" }, { status: 400 });
  }

  sets.push("atualizado_em = now()");
  params.push(id);

  const updated = await sql<Chamado>(
    `update chamados set ${sets.join(", ")} where id = $${i} returning *`,
    params,
  );

  if (updated.length === 0) {
    return Response.json({ error: "não encontrado" }, { status: 404 });
  }

  return Response.json(
    { chamado: updated[0] },
    { headers: { "cache-control": "private, no-store" } },
  );
}
