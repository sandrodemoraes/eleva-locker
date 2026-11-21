"use client";

import { useCallback, useEffect, useState } from "react";
import { ChamadoComposer } from "./ChamadoComposer";
import { ChamadoBoard } from "./ChamadoBoard";
import { AbertosAlert } from "./AbertosAlert";
import { EQUIPE } from "../lib/equipe";
import type { Chamado } from "../lib/types";

type Mode = "campo" | "abertos" | "escritorio";

const TECNICO_KEY = "eleva-tecnico";

export function AppShell() {
  const [mode, setMode] = useState<Mode>("campo");
  const [refreshToken, setRefreshToken] = useState(0);
  const [tecnico, setTecnico] = useState("");
  const [abrindo, setAbrindo] = useState(false);

  useEffect(() => {
    setTecnico(localStorage.getItem(TECNICO_KEY) ?? "");
    if (new URLSearchParams(window.location.search).get("aba") === "abertos") {
      setMode("abertos");
    }
  }, []);

  function escolherTecnico(nome: string) {
    setTecnico(nome);
    if (nome) localStorage.setItem(TECNICO_KEY, nome);
    else localStorage.removeItem(TECNICO_KEY);
  }

  const refresh = useCallback(() => setRefreshToken((n) => n + 1), []);
  const verAbertos = useCallback(() => setMode("abertos"), []);

  function onCreated(_chamado: Chamado) {
    refresh();
  }

  return (
    <div className="shell">
      <header className="top">
        <p className="brand">ELEVA</p>
        <nav className="modes" aria-label="Modo">
          <button
            type="button"
            className={mode === "campo" ? "mode mode--on" : "mode"}
            onClick={() => setMode("campo")}
          >
            Campo
          </button>
          <button
            type="button"
            className={mode === "abertos" ? "mode mode--on" : "mode"}
            onClick={() => setMode("abertos")}
          >
            Em aberto
          </button>
          <button
            type="button"
            className={mode === "escritorio" ? "mode mode--on" : "mode"}
            onClick={() => setMode("escritorio")}
          >
            Escritório
          </button>
        </nav>
      </header>

      <div className="eu-sou">
        <label htmlFor="eu-sou">Eu sou</label>
        <select
          id="eu-sou"
          value={tecnico}
          onChange={(e) => escolherTecnico(e.target.value)}
        >
          <option value="">Escolha seu nome</option>
          {EQUIPE.map((nome) => (
            <option key={nome} value={nome}>
              {nome}
            </option>
          ))}
        </select>
      </div>

      <AbertosAlert onVerAbertos={verAbertos} onChange={refresh} />

      {mode === "campo" && (
        <main className="main main--campo">
          <h1 className="headline">Anote o chamado falando</h1>
          <p className="lede">
            Grave o áudio, marque os funcionários, o horário e envie. No
            escritório dá para editar o chamado durante o serviço.
          </p>
          <ChamadoComposer onCreated={onCreated} />
        </main>
      )}

      {mode === "abertos" && (
        <main className="main">
          <h1 className="headline headline--sm">Chamados em aberto</h1>
          <p className="lede">
            Chamados que o escritório abriu sem técnico. Quem estiver
            disponível toca em “Pegar chamado” e o serviço fica no seu nome.
          </p>
          <ChamadoBoard
            key="abertos"
            refreshToken={refreshToken}
            tecnico={tecnico}
            initialFilter="aberto"
          />
        </main>
      )}

      {mode === "escritorio" && (
        <main className="main">
          <h1 className="headline headline--sm">Fila do escritório</h1>
          <p className="lede">
            Abra chamados para os técnicos, copie o texto pronto e marque
            quando a nota do cliente estiver feita.
          </p>
          {abrindo ? (
            <div className="abrir-box">
              <div className="abrir-head">
                <h2>Abrir chamado</h2>
                <button
                  type="button"
                  className="ghost"
                  onClick={() => setAbrindo(false)}
                >
                  Fechar
                </button>
              </div>
              <ChamadoComposer modo="escritorio" onCreated={onCreated} />
            </div>
          ) : (
            <button
              type="button"
              className="primary abrir-btn"
              onClick={() => setAbrindo(true)}
            >
              + Abrir chamado
            </button>
          )}
          <ChamadoBoard
            key="escritorio"
            refreshToken={refreshToken}
            tecnico={tecnico}
            initialFilter="todos"
          />
        </main>
      )}
    </div>
  );
}
