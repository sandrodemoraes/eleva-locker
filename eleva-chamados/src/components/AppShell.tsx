"use client";

import { useState } from "react";
import { ChamadoComposer } from "./ChamadoComposer";
import { ChamadoBoard } from "./ChamadoBoard";
import type { Chamado } from "../lib/types";

type Mode = "campo" | "escritorio";

export function AppShell() {
  const [mode, setMode] = useState<Mode>("campo");
  const [refreshToken, setRefreshToken] = useState(0);

  function onCreated(_chamado: Chamado) {
    setRefreshToken((n) => n + 1);
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
            className={mode === "escritorio" ? "mode mode--on" : "mode"}
            onClick={() => setMode("escritorio")}
          >
            Escritório
          </button>
        </nav>
      </header>

      {mode === "campo" ? (
        <main className="main main--campo">
          <h1 className="headline">Anote o chamado falando</h1>
          <p className="lede">
            Câmeras, alarme, elétrica ou solar: grave no celular e o
            escritório recebe o texto pronto para a nota do cliente.
          </p>
          <ChamadoComposer onCreated={onCreated} />
        </main>
      ) : (
        <main className="main">
          <h1 className="headline headline--sm">Fila do escritório</h1>
          <p className="lede">
            Copie o texto pronto e marque quando a nota do cliente estiver
            feita.
          </p>
          <ChamadoBoard refreshToken={refreshToken} />
        </main>
      )}
    </div>
  );
}
