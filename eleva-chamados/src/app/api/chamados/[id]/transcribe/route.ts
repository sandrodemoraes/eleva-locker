import { requireIdentity } from "../../../../../../cursor/identity";
import { sql } from "../../../../../lib/db";
import { rateLimit } from "../../../../../lib/rate-limit";
import { transcribeAudioDataUrl } from "../../../../../lib/transcribe";
import type { Chamado } from "../../../../../lib/types";

export const dynamic = "force-dynamic";

export async function POST(
  request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const identity = await requireIdentity(request);
  if (identity instanceof Response) return identity;

  if (!rateLimit(`transcribe-id:${identity.sub}`, 20, 60_000)) {
    return Response.json(
      { error: "Muitas transcrições. Aguarde um minuto." },
      { status: 429 },
    );
  }

  const { id } = await context.params;
  if (!id || id.length > 80) {
    return Response.json({ error: "id inválido" }, { status: 400 });
  }

  const rows = await sql<Chamado>(`select * from chamados where id = $1`, [id]);
  if (rows.length === 0) {
    return Response.json({ error: "não encontrado" }, { status: 404 });
  }

  const chamado = rows[0];
  const audio = chamado.audio_base64 || "";
  if (!audio.startsWith("data:audio/")) {
    return Response.json(
      { error: "Este chamado não tem áudio para transcrever" },
      { status: 400 },
    );
  }

  const result = await transcribeAudioDataUrl(audio);
  if (!result.text && result.source === "none") {
    return Response.json(
      {
        error:
          "Falta a chave OpenAI nas Secrets do app para transcrever o áudio.",
        needs_key: true,
      },
      { status: 503 },
    );
  }
  if (!result.text) {
    return Response.json(
      { error: result.error || "Falha na transcrição" },
      { status: 502 },
    );
  }

  const text = result.text.slice(0, 4000);
  const updated = await sql<Chamado>(
    `update chamados
     set transcricao = $1,
         descricao = case when coalesce(descricao, '') = '' then $1 else descricao end,
         atualizado_em = now()
     where id = $2
     returning *`,
    [text, id],
  );

  return Response.json(
    { chamado: updated[0], text },
    { headers: { "cache-control": "private, no-store" } },
  );
}
