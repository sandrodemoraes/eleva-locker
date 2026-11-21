import { requireIdentity } from "../../../../cursor/identity";
import { rateLimit } from "../../../lib/rate-limit";
import { transcribeAudioDataUrl } from "../../../lib/transcribe";

export const dynamic = "force-dynamic";

const MAX_BODY = 1_200_000; // ~900KB data-url + margem

export async function POST(request: Request) {
  const identity = await requireIdentity(request);
  if (identity instanceof Response) return identity;

  if (!rateLimit(`transcribe:${identity.sub}`, 20, 60_000)) {
    return Response.json(
      { error: "Muitas transcrições. Aguarde um minuto." },
      { status: 429 },
    );
  }

  const lengthHeader = request.headers.get("content-length");
  if (lengthHeader) {
    const n = Number(lengthHeader);
    if (Number.isFinite(n) && n > MAX_BODY) {
      return Response.json({ error: "Áudio grande demais" }, { status: 413 });
    }
  }

  let body: { audio_base64?: string };
  try {
    body = (await request.json()) as { audio_base64?: string };
  } catch {
    return Response.json({ error: "JSON inválido" }, { status: 400 });
  }

  const audio = typeof body.audio_base64 === "string" ? body.audio_base64 : "";
  if (!audio.startsWith("data:audio/")) {
    return Response.json({ error: "Envie o áudio gravado" }, { status: 400 });
  }
  if (audio.length > 900_000) {
    return Response.json({ error: "Áudio grande demais" }, { status: 413 });
  }

  const result = await transcribeAudioDataUrl(audio);
  if (!result.text && result.source === "none") {
    return Response.json(
      {
        text: "",
        source: "none",
        needs_key: true,
        hint: "Para o áudio virar texto sozinho, adicione a chave OpenAI nas Secrets do app. Enquanto isso, digite o que foi falado.",
      },
      { headers: { "cache-control": "private, no-store" } },
    );
  }
  if (!result.text && result.error) {
    return Response.json(
      { error: result.error, text: "", source: result.source },
      { status: 502, headers: { "cache-control": "private, no-store" } },
    );
  }

  return Response.json(
    { text: result.text, source: result.source },
    { headers: { "cache-control": "private, no-store" } },
  );
}
