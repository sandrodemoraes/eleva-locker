"use client";

import { useState, useTransition } from "react";
import { VoiceCapture } from "./VoiceCapture";
import { EquipePicker } from "./EquipePicker";
import { parseChamadoFromSpeech } from "../lib/parse-chamado";
import type { Chamado, ChamadoInput, Urgencia } from "../lib/types";
import { SERVICOS } from "../lib/types";

type Props = {
  onCreated: (chamado: Chamado) => void;
  modo?: "campo" | "escritorio";
};

const empty: ChamadoInput = {
  cliente: "",
  quem_chamou: "",
  telefone: "",
  endereco: "",
  servico: "Outro",
  urgencia: "normal",
  descricao: "",
  transcricao: "",
  audio_base64: "",
  funcionarios: "",
  horario: "",
  marcado: false,
};

function mergeParsed(prev: ChamadoInput, transcript: string): ChamadoInput {
  const parsed = parseChamadoFromSpeech(transcript);
  return {
    ...prev,
    transcricao: transcript,
    descricao: transcript,
    cliente: parsed.cliente || prev.cliente,
    quem_chamou: parsed.quem_chamou || prev.quem_chamou,
    telefone: parsed.telefone || prev.telefone,
    endereco: parsed.endereco || prev.endereco,
    servico:
      parsed.servico !== "Outro" ? parsed.servico : prev.servico || "Outro",
    urgencia:
      parsed.urgencia !== "normal" ? parsed.urgencia : prev.urgencia,
    funcionarios: parsed.funcionarios || prev.funcionarios,
    horario: parsed.horario || prev.horario,
  };
}

export function ChamadoComposer({ onCreated, modo = "campo" }: Props) {
  const [form, setForm] = useState<ChamadoInput>(empty);
  const [aberto, setAberto] = useState(modo === "escritorio");
  const [interim, setInterim] = useState("");
  const [message, setMessage] = useState("");
  const [transcribing, setTranscribing] = useState(false);
  const [pending, startTransition] = useTransition();

  function onTranscript(text: string, isFinal: boolean) {
    if (isFinal) {
      setInterim("");
      setForm((prev) => {
        const nextTranscript = `${prev.transcricao} ${text}`.trim();
        return mergeParsed(prev, nextTranscript);
      });
    } else {
      setInterim(text);
    }
  }

  async function onAudio(dataUrl: string) {
    setForm((prev) => ({ ...prev, audio_base64: dataUrl }));
    setTranscribing(true);
    setMessage("Passando o áudio para texto…");
    try {
      const res = await fetch("/api/transcribe", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ audio_base64: dataUrl }),
      });
      const data = (await res.json().catch(() => ({}))) as {
        text?: string;
        source?: string;
        hint?: string;
        error?: string;
        needs_key?: boolean;
      };
      if (data.text?.trim()) {
        setForm((prev) => {
          const merged = mergeParsed(prev, data.text!.trim());
          return { ...merged, audio_base64: dataUrl };
        });
        setMessage("Áudio convertido em texto. Revise e envie.");
      } else if (data.needs_key || data.source === "none") {
        setMessage(
          data.hint ||
            "Digite o texto do áudio abaixo. A transcrição automática precisa da chave OpenAI nas Secrets.",
        );
      } else if (data.error) {
        setMessage(data.error);
      }
    } catch {
      setMessage("Não deu para transcrever agora. Digite o texto do áudio.");
    } finally {
      setTranscribing(false);
    }
  }

  function update<K extends keyof ChamadoInput>(key: K, value: ChamadoInput[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function onTranscricaoEdit(value: string) {
    setForm((prev) => mergeParsed(prev, value));
  }

  function salvar() {
    setMessage("");
    startTransition(async () => {
      const res = await fetch("/api/chamados", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ ...form, aberto }),
      });
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as { error?: string };
        setMessage(data.error || "Não foi possível salvar");
        return;
      }
      const data = (await res.json()) as { chamado: Chamado };
      onCreated(data.chamado);
      setForm(empty);
      setInterim("");
      setMessage(
        aberto
          ? "Chamado aberto. Os técnicos recebem o aviso para pegar."
          : "Chamado anotado. O escritório já pode fazer a nota.",
      );
    });
  }

  const canSend =
    Boolean(form.descricao || form.cliente || form.audio_base64);

  return (
    <section className="composer">
      <VoiceCapture
        onTranscript={onTranscript}
        onAudio={(dataUrl) => void onAudio(dataUrl)}
        disabled={pending || transcribing}
      />

      {form.audio_base64 && (
        <audio controls src={form.audio_base64} className="audio-preview" />
      )}

      <label className="field">
        <span>Texto do áudio</span>
        <textarea
          rows={4}
          value={`${form.transcricao}${interim ? ` ${interim}` : ""}`.trim()}
          onChange={(e) => onTranscricaoEdit(e.target.value)}
          placeholder="O que foi falado aparece aqui…"
        />
      </label>

      <div className="grid-2">
        <label className="field">
          <span>Cliente</span>
          <input
            value={form.cliente}
            onChange={(e) => update("cliente", e.target.value)}
            placeholder="Empresa ou nome"
          />
        </label>
        <label className="field">
          <span>Quem chamou</span>
          <input
            value={form.quem_chamou}
            onChange={(e) => update("quem_chamou", e.target.value)}
            placeholder="Pessoa que ligou"
          />
        </label>
      </div>

      <div className="grid-2">
        <label className="field">
          <span>Telefone</span>
          <input
            value={form.telefone}
            onChange={(e) => update("telefone", e.target.value)}
            placeholder="WhatsApp"
            inputMode="tel"
          />
        </label>
        <label className="field">
          <span>Horário</span>
          <input
            type="datetime-local"
            value={form.horario}
            onChange={(e) => update("horario", e.target.value)}
          />
        </label>
      </div>

      <label className="field">
        <span>Endereço</span>
        <input
          value={form.endereco}
          onChange={(e) => update("endereco", e.target.value)}
          placeholder="Rua, número, bairro"
        />
      </label>

      <label className="check-row check-row--solo" htmlFor="aberto-novo">
        <input
          id="aberto-novo"
          type="checkbox"
          checked={aberto}
          disabled={pending || transcribing}
          onChange={(e) => setAberto(e.target.checked)}
        />
        <span>Deixar em aberto para o técnico disponível</span>
      </label>

      {!aberto && (
        <EquipePicker
          value={form.funcionarios}
          onChange={(v) => update("funcionarios", v)}
          disabled={pending || transcribing}
        />
      )}

      <label className="check-row check-row--solo" htmlFor="marcado-novo">
        <input
          id="marcado-novo"
          type="checkbox"
          checked={form.marcado}
          disabled={pending || transcribing}
          onChange={(e) => update("marcado", e.target.checked)}
        />
        <span>Marcado / confirmado</span>
      </label>

      <div className="grid-2">
        <label className="field">
          <span>Serviço</span>
          <select
            value={form.servico}
            onChange={(e) => update("servico", e.target.value)}
          >
            {SERVICOS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Urgência</span>
          <select
            value={form.urgencia}
            onChange={(e) => update("urgencia", e.target.value as Urgencia)}
          >
            <option value="baixa">Baixa</option>
            <option value="normal">Normal</option>
            <option value="alta">Alta</option>
          </select>
        </label>
      </div>

      <button
        type="button"
        className="primary"
        disabled={pending || transcribing || !canSend}
        onClick={salvar}
      >
        {pending
          ? "Salvando…"
          : transcribing
            ? "Transcrevendo…"
            : aberto
              ? "Abrir chamado para os técnicos"
              : "Enviar para o escritório"}
      </button>
      {message && <p className="toast">{message}</p>}
    </section>
  );
}
