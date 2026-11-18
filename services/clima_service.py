"""Clima local para Eleva Cam — Open-Meteo (stdlib, sem chave)."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

# Cache simples em memória: (lat, lon) -> (expires_at, payload)
_CACHE: dict[tuple[float, float], tuple[float, dict[str, Any]]] = {}
_CACHE_TTL_SEG = 600  # 10 min
_TIMEOUT = 4


def _rotulo_codigo(codigo: Optional[int]) -> str:
    if codigo is None:
        return ""
    if codigo == 0:
        return "Céu limpo"
    if codigo in (1, 2):
        return "Parcialmente nublado"
    if codigo == 3:
        return "Nublado"
    if codigo in (45, 48):
        return "Neblina"
    if codigo in (51, 53, 55, 56, 57):
        return "Garoa"
    if codigo in (61, 63, 65, 66, 67, 80, 81, 82):
        return "Chuva"
    if codigo in (71, 73, 75, 77, 85, 86):
        return "Neve"
    if codigo in (95, 96, 99):
        return "Tempestade"
    return "Condições variáveis"


def buscar_clima(latitude, longitude) -> Optional[dict[str, Any]]:
    """Retorna temperatura e resumo no ponto da câmera, ou None se falhar."""
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return None

    chave = (round(lat, 4), round(lon, 4))
    agora = time.time()
    cached = _CACHE.get(chave)
    if cached and cached[0] > agora:
        return cached[1]

    try:
        qs = urllib.parse.urlencode(
            {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m",
                "timezone": "America/Sao_Paulo",
            }
        )
        url = f"https://api.open-meteo.com/v1/forecast?{qs}"
        req = urllib.request.Request(url, headers={"User-Agent": "elevacam/1.0"})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        atual = (data or {}).get("current") or {}
        temp = atual.get("temperature_2m")
        if temp is None:
            return None

        payload = {
            "temperatura_c": round(float(temp)),
            "umidade": atual.get("relative_humidity_2m"),
            "vento_kmh": (
                round(float(atual["wind_speed_10m"]))
                if atual.get("wind_speed_10m") is not None
                else None
            ),
            "resumo": _rotulo_codigo(atual.get("weather_code")),
        }
        _CACHE[chave] = (agora + _CACHE_TTL_SEG, payload)
        return payload
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError, KeyError):
        return None
    except Exception:
        return None
