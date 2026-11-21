import { requireIdentity } from "../../../../../../cursor/identity";
import { sql } from "../../../../../lib/db";
import type { Chamado } from "../../../../../lib/types";

export const dynamic = "force-dynamic";

export async function POST(
  request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const identity = await requireIdentity(request);
  if (identity instanceof Response) return identity;

  const { id } = await context.params;
  if (!id || id.length > 80) {
    return Response.json({ error: "id inválido" }, { status: 400 });
  }

  let body: { tecnico?: string };
  try {
    body = (await request.json()) as { tecnico?: string };
  } catch {
    return Response.json({ error: "JSON inválido" }, { status: 400 });
  }

  const tecnico =
    typeof body.tecnico === "string" ? body.tecnico.trim().slice(0, 120) : "";
  if (!tecnico) {
    return Response.json({ error: "Escolha o técnico" }, { status: 400 });
  }

  // Só pega se ainda estiver em aberto: dois técnicos não ficam com o mesmo chamado.
  const updated = await sql<Chamado>(
    `update chamados
     set status = 'em_andamento',
         funcionarios = $1,
         assumido_por = $1,
         assumido_em = now(),
         atualizado_em = now()
     where id = $2 and status = 'aberto'
     returning *`,
    [tecnico, id],
  );

  if (updated.length === 0) {
    const rows = await sql<Chamado>(
      `select assumido_por from chamados where id = $1`,
      [id],
    );
    if (rows.length === 0) {
      return Response.json({ error: "não encontrado" }, { status: 404 });
    }
    return Response.json(
      {
        error: rows[0].assumido_por
          ? `Já foi pego por ${rows[0].assumido_por}`
          : "Este chamado não está mais em aberto",
      },
      { status: 409 },
    );
  }

  return Response.json(
    { chamado: updated[0] },
    { headers: { "cache-control": "private, no-store" } },
  );
}
