"use client";

import { useCallback, useEffect, useState, useTransition } from "react";
import type { Chamado, ChamadoStatus } from "../lib/types";
import { textoParaNota } from "../lib/parse-chamado";

const FILTERS: { id: string; label: string; status?: ChamadoStatus }[] = [
  { id: "todos", label: "Todos" },
  { id: "aguardando_nota", label: "Aguardando nota", status: "aguardando_nota" },
  { id: "nota_feita", label: "Nota feita", status: "nota_feita" },
  { id: "concluido", label: "Concluídos", status: "concluido" },
];

function formatWhen(iso: string) {
  try {
    return new Intl.DateTimeFormat("pt-BR", {
      timeZone: "America/Sao_Paulo",
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

type Props = {
  refreshToken: number;
};

export function ChamadoBoard({ refreshToken }: Props) {
  const [filter, setFilter] = useState("aguardando_nota");
  const [items, setItems] = useState<Chamado[]>([]);
  const [error, setError] = useState("");
  const [pending, startTransition] = useTransition();
  const [copied, setCopied] = useState<string | null>(null);

  const load = useCallback(() => {
    startTransition(async () => {
      setError("");
      const q =
        filter === "todos" ? "" : `?status=${encodeURIComponent(filter)}`;
      const res = await fetch(`/api/chamados${q}`);
      if (!res.ok) {
        setError("Não foi possível carregar os chamados.");
        return;
      }
      const data = (await res.json()) as { chamados: Chamado[] };
      setItems(data.chamados);
    });
  }, [filter]);

  useEffect(() => {
    load();
  }, [load, refreshToken]);

  async function setStatus(id: string, status: ChamadoStatus) {
    const res = await fetch(`/api/chamados/${id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ status }),
    });
    if (res.ok) load();
  }

  async function copyNota(c: Chamado) {
    const text = textoParaNota(c);
    try {
      await navigator.clipboard.writeText(text);
      setCopied(c.id);
      setTimeout(() => setCopied(null), 2000);
    } catch {
      setError("Não foi possível copiar. Selecione o texto manualmente.");
    }
  }

  return (
    <section className="board">
      <div className="filters" role="tablist">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            type="button"
            role="tab"
            aria-selected={filter === f.id}
            className={filter === f.id ? "chip chip--on" : "chip"}
            onClick={() => setFilter(f.id)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {pending && items.length === 0 && <p className="hint">Carregando…</p>}
      {error && <p className="error">{error}</p>}

      <ul className="chamado-list">
        {items.map((c) => (
          <li key={c.id} className="chamado-item">
            <header className="chamado-head">
              <div>
                <h3>{c.cliente || "Cliente sem nome"}</h3>
                <p className="meta">
                  {c.servico} · {formatWhen(c.criado_em)} · {c.criado_por_nome}
                </p>
              </div>
              <span className={`badge badge--${c.urgencia}`}>{c.urgencia}</span>
            </header>
            <p className="endereco">{c.endereco || "Sem endereço"}</p>
            {c.telefone && <p className="fone">{c.telefone}</p>}
            {c.audio_base64 && (
              <audio controls src={c.audio_base64} className="audio-preview" />
            )}
            <pre className="nota-preview">{textoParaNota(c)}</pre>
            <div className="actions">
              <button type="button" className="ghost" onClick={() => copyNota(c)}>
                {copied === c.id ? "Copiado" : "Copiar para nota"}
              </button>
              {c.status === "aguardando_nota" && (
                <button
                  type="button"
                  className="ghost"
                  onClick={() => setStatus(c.id, "nota_feita")}
                >
                  Marcar nota feita
                </button>
              )}
              {c.status === "nota_feita" && (
                <button
                  type="button"
                  className="ghost"
                  onClick={() => setStatus(c.id, "concluido")}
                >
                  Concluir
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>

      {!pending && items.length === 0 && (
        <p className="empty">Nenhum chamado neste filtro.</p>
      )}
    </section>
  );
}
