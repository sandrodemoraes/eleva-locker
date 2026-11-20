/** Transcreve áudio (data URL) com Whisper quando OPENAI_API_KEY está definida. */

export async function transcribeAudioDataUrl(
  dataUrl: string,
): Promise<{ text: string; source: "whisper" | "none"; error?: string }> {
  const key = process.env.OPENAI_API_KEY?.trim() ?? "";
  if (!key) {
    return { text: "", source: "none" };
  }
  if (!dataUrl.startsWith("data:audio/")) {
    return { text: "", source: "none", error: "áudio inválido" };
  }

  const comma = dataUrl.indexOf(",");
  if (comma < 0) {
    return { text: "", source: "none", error: "áudio inválido" };
  }
  const meta = dataUrl.slice(5, comma); // audio/webm;base64
  const mime = meta.split(";")[0] || "audio/webm";
  const b64 = dataUrl.slice(comma + 1);
  const bytes = Buffer.from(b64, "base64");
  if (bytes.length < 200) {
    return { text: "", source: "none", error: "áudio muito curto" };
  }
  if (bytes.length > 20 * 1024 * 1024) {
    return { text: "", source: "none", error: "áudio muito grande" };
  }

  const ext = mime.includes("ogg")
    ? "ogg"
    : mime.includes("mp4") || mime.includes("m4a")
      ? "m4a"
      : mime.includes("wav")
        ? "wav"
        : "webm";

  const form = new FormData();
  form.append(
    "file",
    new Blob([new Uint8Array(bytes)], { type: mime }),
    `chamado.${ext}`,
  );
  form.append("model", "whisper-1");
  form.append("language", "pt");
  form.append("response_format", "json");

  const res = await fetch("https://api.openai.com/v1/audio/transcriptions", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}` },
    body: form,
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    return {
      text: "",
      source: "whisper",
      error: `falha na transcrição (${res.status})${detail ? `: ${detail.slice(0, 120)}` : ""}`,
    };
  }

  const data = (await res.json()) as { text?: string };
  return { text: (data.text || "").trim(), source: "whisper" };
}
