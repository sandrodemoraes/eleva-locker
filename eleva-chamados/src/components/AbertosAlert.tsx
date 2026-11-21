"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Chamado } from "../lib/types";

const POLL_MS = 20_000;
const BASE_TITLE = "Eleva Chamados";

type Props = {
  onVerAbertos: () => void;
  onChange: () => void;
};

type Permissao = NotificationPermission | "indisponivel";

function permissaoAtual(): Permissao {
  if (typeof window === "undefined" || !("Notification" in window)) {
    return "indisponivel";
  }
  return Notification.permission;
}

async function registrarSW(): Promise<ServiceWorkerRegistration | null> {
  if (!("serviceWorker" in navigator)) return null;
  try {
    return await navigator.serviceWorker.register("/sw.js");
  } catch {
    return null;
  }
}

async function avisar(chamado: Chamado, total: number) {
  if (permissaoAtual() !== "granted") return;
  const titulo = "Chamado técnico em aberto";
  const corpo = [chamado.cliente || "Cliente não informado", chamado.servico, chamado.endereco]
    .filter(Boolean)
    .join(" · ");
  const opcoes: NotificationOptions = {
    body: total > 1 ? `${corpo}\n${total} chamados aguardando técnico` : corpo,
    tag: `chamado-${chamado.id}`,
    icon: "/favicon.ico",
  };
  const reg = await registrarSW();
  if (reg) {
    await reg.showNotification(titulo, opcoes);
  } else {
    new Notification(titulo, opcoes);
  }
}

export function AbertosAlert({ onVerAbertos, onChange }: Props) {
  const [abertos, setAbertos] = useState<Chamado[]>([]);
  const [permissao, setPermissao] = useState<Permissao>("default");
  const conhecidos = useRef<Set<string> | null>(null);

  const verificar = useCallback(async () => {
    try {
      const res = await fetch("/api/chamados?status=aberto&resumo=1", { cache: "no-store" });
      if (!res.ok) return;
      const data = (await res.json()) as { chamados: Chamado[] };
      const lista = data.chamados ?? [];
      const ids = new Set(lista.map((c) => c.id));
      const antes = conhecidos.current;
      if (antes) {
        const novos = lista.filter((c) => !antes.has(c.id));
        for (const c of novos) void avisar(c, lista.length);
        const mudou = novos.length > 0 || [...antes].some((id) => !ids.has(id));
        if (mudou) onChange();
      }
      conhecidos.current = ids;
      setAbertos(lista);
    } catch {
      // sem rede: tenta de novo no próximo ciclo
    }
  }, [onChange]);

  useEffect(() => {
    setPermissao(permissaoAtual());
    if (permissaoAtual() === "granted") void registrarSW();
    void verificar();
    const timer = window.setInterval(() => void verificar(), POLL_MS);
    const onVisible = () => {
      if (document.visibilityState === "visible") void verificar();
    };
    document.addEventListener("visibilitychange", onVisible);
    const onMessage = (e: MessageEvent) => {
      if (e.data?.type === "abrir-abertos") onVerAbertos();
    };
    navigator.serviceWorker?.addEventListener("message", onMessage);
    return () => {
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisible);
      navigator.serviceWorker?.removeEventListener("message", onMessage);
    };
  }, [verificar, onVerAbertos]);

  useEffect(() => {
    document.title = abertos.length ? `(${abertos.length}) ${BASE_TITLE}` : BASE_TITLE;
  }, [abertos.length]);

  async function ativar() {
    if (permissaoAtual() === "indisponivel") return;
    const result = await Notification.requestPermission();
    setPermissao(result);
    if (result === "granted") {
      const reg = await registrarSW();
      const opcoes = { body: "Você vai receber um aviso quando abrirem um chamado técnico." };
      if (reg) await reg.showNotification("Avisos ativados", opcoes);
      else new Notification("Avisos ativados", opcoes);
    }
  }

  const n = abertos.length;

  return (
    <div className={n ? "alerta alerta--on" : "alerta"} role="status">
      <p className="alerta-texto">
        {n === 0
          ? "Nenhum chamado técnico em aberto."
          : n === 1
            ? "1 chamado técnico em aberto esperando técnico."
            : `${n} chamados técnicos em aberto esperando técnico.`}
      </p>
      <div className="alerta-acoes">
        {n > 0 && (
          <button type="button" className="chip" onClick={onVerAbertos}>
            Ver e pegar
          </button>
        )}
        {permissao === "default" && (
          <button type="button" className="chip" onClick={() => void ativar()}>
            Ativar avisos no celular
          </button>
        )}
        {permissao === "denied" && (
          <span className="alerta-nota">
            Avisos bloqueados no navegador. Libere nas configurações do site.
          </span>
        )}
      </div>
    </div>
  );
}
