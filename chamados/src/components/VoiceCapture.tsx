"use client";

import { useEffect, useRef, useState } from "react";

type SpeechRecognitionLike = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
};

type SpeechRecognitionEventLike = {
  resultIndex: number;
  results: ArrayLike<{
    isFinal: boolean;
    0: { transcript: string };
  }>;
};

declare global {
  interface Window {
    webkitSpeechRecognition?: new () => SpeechRecognitionLike;
    SpeechRecognition?: new () => SpeechRecognitionLike;
  }
}

type Props = {
  onTranscript: (text: string, isFinal: boolean) => void;
  disabled?: boolean;
};

export function VoiceCapture({ onTranscript, disabled }: Props) {
  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [error, setError] = useState("");
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const wantListen = useRef(false);

  useEffect(() => {
    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    setSupported(Boolean(Ctor));
  }, []);

  useEffect(() => {
    return () => {
      wantListen.current = false;
      recognitionRef.current?.stop();
    };
  }, []);

  function start() {
    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Ctor) {
      setError("Seu navegador não suporta ditado por voz. Use Chrome no celular.");
      return;
    }
    setError("");
    const recognition = new Ctor();
    recognition.lang = "pt-BR";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = (event) => {
      let interim = "";
      let finalChunk = "";
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const piece = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalChunk += piece;
        else interim += piece;
      }
      if (finalChunk) onTranscript(finalChunk, true);
      else if (interim) onTranscript(interim, false);
    };
    recognition.onerror = (event) => {
      if (event.error === "not-allowed") {
        setError("Permita o microfone para anotar por áudio.");
      } else if (event.error !== "aborted") {
        setError(`Falha no microfone: ${event.error}`);
      }
      wantListen.current = false;
      setListening(false);
    };
    recognition.onend = () => {
      if (wantListen.current) {
        try {
          recognition.start();
        } catch {
          setListening(false);
        }
      } else {
        setListening(false);
      }
    };
    recognitionRef.current = recognition;
    wantListen.current = true;
    recognition.start();
    setListening(true);
  }

  function stop() {
    wantListen.current = false;
    recognitionRef.current?.stop();
    setListening(false);
  }

  return (
    <div className="voice">
      <button
        type="button"
        className={`mic-btn ${listening ? "mic-btn--live" : ""}`}
        disabled={disabled || !supported}
        onClick={() => (listening ? stop() : start())}
        aria-pressed={listening}
      >
        <span className="mic-pulse" aria-hidden />
        <span className="mic-label">
          {listening ? "Parar áudio" : "Falar chamado"}
        </span>
      </button>
      {!supported && (
        <p className="hint">
          Ditado por voz precisa do Chrome (Android/desktop). Você ainda pode digitar.
        </p>
      )}
      {error && <p className="error">{error}</p>}
      {listening && (
        <p className="hint hint--live">Ouvindo… diga cliente, endereço e serviço.</p>
      )}
    </div>
  );
}
