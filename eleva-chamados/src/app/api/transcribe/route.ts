import { requireIdentity } from "../../../../cursor/identity";
import { transcribeAudioDataUrl } from "../../../lib/transcribe";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const identity = await requireIdentity(request);
  if (identity instanceof Response) return identity;

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

  const result = await transcribeAudioDataUrl(audio);
  if (!result.text && result.source === "none") {
    return Response.json(
      {
        text: "",
        source: "none",
        hint: "Ditado do Chrome ou digite o texto. Com OPENAI_API_KEY o áudio vira texto automático.",
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
