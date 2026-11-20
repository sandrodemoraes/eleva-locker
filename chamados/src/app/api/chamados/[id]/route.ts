import { requireIdentity } from "../../../../../cursor/identity";
import { sql } from "../../../../lib/db";
import type { Chamado, ChamadoStatus } from "../../../../lib/types";

export const dynamic = "force-dynamic";

const STATUSES: ChamadoStatus[] = [
  "aguardando_nota",
  "nota_feita",
  "concluido",
  "cancelado",
];

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

  let body: { status?: string };
  try {
    body = (await request.json()) as { status?: string };
  } catch {
    return Response.json({ error: "JSON inválido" }, { status: 400 });
  }

  const status = body.status;
  if (!status || !STATUSES.includes(status as ChamadoStatus)) {
    return Response.json({ error: "status inválido" }, { status: 400 });
  }

  const updated = await sql<Chamado>(
    `update chamados
     set status = $1, atualizado_em = now()
     where id = $2
     returning *`,
    [status, id],
  );

  if (updated.length === 0) {
    return Response.json({ error: "não encontrado" }, { status: 404 });
  }

  return Response.json(
    { chamado: updated[0] },
    { headers: { "cache-control": "private, no-store" } },
  );
}
