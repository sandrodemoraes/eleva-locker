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
  onAudio?: (dataUrl: string) => void;
  disabled?: boolean;
};

const MAX_AUDIO_CHARS = 900_000; // ~675KB base64 — cabe no JSON sem estourar

async function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(blob);
  });
}

export function VoiceCapture({ onTranscript, onAudio, disabled }: Props) {
  const [speechOk, setSpeechOk] = useState(false);
  const [micOk, setMicOk] = useState(false);
  const [listening, setListening] = useState(false);
  const [error, setError] = useState("");
  const [hasAudio, setHasAudio] = useState(false);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const wantListen = useRef(false);

  useEffect(() => {
    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    setSpeechOk(Boolean(Ctor));
    setMicOk(Boolean(navigator.mediaDevices?.getUserMedia));
  }, []);

  useEffect(() => {
    return () => {
      wantListen.current = false;
      recognitionRef.current?.stop();
      mediaRecorderRef.current?.stop();
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  async function start() {
    setError("");
    setHasAudio(false);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "";
      const recorder = mime
        ? new MediaRecorder(stream, { mimeType: mime })
        : new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });
        if (blob.size === 0 || !onAudio) return;
        try {
          const dataUrl = await blobToDataUrl(blob);
          if (dataUrl.length <= MAX_AUDIO_CHARS) {
            onAudio(dataUrl);
            setHasAudio(true);
          } else {
            setError("Áudio longo demais; a transcrição ainda foi salva.");
          }
        } catch {
          setError("Não foi possível guardar o áudio.");
        }
      };
      mediaRecorderRef.current = recorder;
      recorder.start(1000);
    } catch {
      setError("Permita o microfone para anotar por áudio.");
      return;
    }

    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (Ctor) {
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
          wantListen.current = false;
          setListening(false);
        } else if (event.error !== "aborted" && event.error !== "no-speech") {
          // gravação continua mesmo se o ditado falhar
          setError(
            "Ditado indisponível neste momento — revise o texto ou digite.",
          );
        }
      };
      recognition.onend = () => {
        if (wantListen.current) {
          try {
            recognition.start();
          } catch {
            /* ignore restart race */
          }
        }
      };
      recognitionRef.current = recognition;
      try {
        recognition.start();
      } catch {
        /* MediaRecorder still running */
      }
    }

    wantListen.current = true;
    setListening(true);
  }

  function stop() {
    wantListen.current = false;
    recognitionRef.current?.stop();
    recognitionRef.current = null;
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
    mediaRecorderRef.current = null;
    setListening(false);
  }

  const canRecord = micOk;

  return (
    <div className="voice">
      <button
        type="button"
        className={`mic-btn ${listening ? "mic-btn--live" : ""}`}
        disabled={disabled || !canRecord}
        onClick={() => (listening ? stop() : void start())}
        aria-pressed={listening}
      >
        <span className="mic-pulse" aria-hidden />
        <span className="mic-label">
          {listening ? "Parar áudio" : "Falar chamado"}
        </span>
      </button>
      {!canRecord && (
        <p className="hint">
          Microfone indisponível neste navegador. Você ainda pode digitar.
        </p>
      )}
      {canRecord && !speechOk && (
        <p className="hint">
          Neste navegador o áudio é gravado; digite ou revise o texto depois.
          No Chrome o ditado preenche sozinho.
        </p>
      )}
      {error && <p className="error">{error}</p>}
      {listening && (
        <p className="hint hint--live">
          Ouvindo… diga cliente, endereço e serviço.
        </p>
      )}
      {hasAudio && !listening && (
        <p className="toast">Áudio anexado para o escritório ouvir.</p>
      )}
    </div>
  );
}
