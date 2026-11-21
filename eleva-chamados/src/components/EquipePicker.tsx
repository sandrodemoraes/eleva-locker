"use client";

import { EQUIPE, joinFuncionarios, parseFuncionarios } from "../lib/equipe";

type Props = {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
};

export function EquipePicker({ value, onChange, disabled }: Props) {
  const selected = new Set(parseFuncionarios(value));

  function toggle(name: string) {
    const next = new Set(selected);
    if (next.has(name)) next.delete(name);
    else next.add(name);
    onChange(joinFuncionarios([...next]));
  }

  return (
    <fieldset className="equipe" disabled={disabled}>
      <legend className="equipe-label">Funcionários (marque quem vai)</legend>
      <div className="equipe-list">
        {EQUIPE.map((name) => {
          const on = selected.has(name);
          const id = `func-${name.replace(/\s+/g, "-").toLowerCase()}`;
          return (
            <label key={name} className="check-row" htmlFor={id}>
              <input
                id={id}
                type="checkbox"
                checked={on}
                disabled={disabled}
                onChange={() => toggle(name)}
              />
              <span>{name}</span>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}
