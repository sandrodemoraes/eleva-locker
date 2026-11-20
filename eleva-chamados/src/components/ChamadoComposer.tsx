"use client";

import { useState, useTransition } from "react";
import { VoiceCapture } from "./VoiceCapture";
import { parseChamadoFromSpeech } from "../lib/parse-chamado";
import type { Chamado, ChamadoInput, Urgencia } from "../lib/types";
import { SERVICOS } from "../lib/types";

type Props = {
  onCreated: (chamado: Chamado) => void;
};

const empty: ChamadoInput = {
  cliente: "",
  telefone: "",
  endereco: "",
  servico: "Outro",
  urgencia: "normal",
  descricao: "",
  transcricao: "",
  audio_base64: "",
};

function mergeParsed(prev: ChamadoInput, transcript: string): ChamadoInput {
  const parsed = parseChamadoFromSpeech(transcript);
  return {
    ...prev,
    transcricao: transcript,
    descricao: transcript,
    cliente: parsed.cliente || prev.cliente,
    telefone: parsed.telefone || prev.telefone,
    endereco: parsed.endereco || prev.endereco,
    servico:
      parsed.servico !== "Outro" ? parsed.servico : prev.servico || "Outro",
    urgencia:
      parsed.urgencia !== "normal" ? parsed.urgencia : prev.urgencia,
  };
}

export function ChamadoComposer({ onCreated }: Props) {
  const [form, setForm] = useState<ChamadoInput>(empty);
  const [interim, setInterim] = useState("");
  const [message, setMessage] = useState("");
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
        body: JSON.stringify(form),
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
      setMessage("Chamado anotado. O escritório já pode fazer a nota.");
    });
  }

  const canSend =
    Boolean(form.descricao || form.cliente || form.audio_base64);

  return (
    <section className="composer">
      <VoiceCapture
        onTranscript={onTranscript}
        onAudio={(dataUrl) => update("audio_base64", dataUrl)}
        disabled={pending}
      />

      {form.audio_base64 && (
        <audio controls src={form.audio_base64} className="audio-preview" />
      )}

      <label className="field">
        <span>Transcrição</span>
        <textarea
          rows={4}
          value={`${form.transcricao}${interim ? ` ${interim}` : ""}`.trim()}
          onChange={(e) => onTranscricaoEdit(e.target.value)}
          placeholder="Ex.: Cliente Maria, telefone 11 98888-0000, rua das Acácias 45, instalação de câmeras, urgência alta"
        />
      </label>

      <div className="grid-2">
        <label className="field">
          <span>Cliente</span>
          <input
            value={form.cliente}
            onChange={(e) => update("cliente", e.target.value)}
            placeholder="Nome"
          />
        </label>
        <label className="field">
          <span>Telefone</span>
          <input
            value={form.telefone}
            onChange={(e) => update("telefone", e.target.value)}
            placeholder="WhatsApp"
            inputMode="tel"
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
        disabled={pending || !canSend}
        onClick={salvar}
      >
        {pending ? "Salvando…" : "Enviar para o escritório"}
      </button>
      {message && <p className="toast">{message}</p>}
    </section>
  );
}
