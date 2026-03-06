---
name: ghost-cleanup
description: Limpieza quirúrgica de deuda técnica. Detecta archivos (JS, TS, PY) y assets (PNG, JPG, WOFF) que nadie usa mediante análisis de Grafo de Referencias Estático.
---

# Ghost Cleanup (The Debt Reaper)

Herramienta para limpiar proyectos de archivos y assets huérfanos. No usa heurísticas vagas; rastrea imports reales desde los entry points.

## Instalación rápida (CLI)

```bash
npx skills add https://github.com/joaquinescalante23/toolbox --skill ghost-cleanup
```

## Workflow

### 1. Auditoría (Escaneo)
Rastrea el grafo de dependencias para encontrar archivos inalcanzables.
- **Comando:** `python3 scripts/ghost_scanner.py --root <directorio_proyecto>`
- **Output:** Genera `ghost_report.json` con la lista de candidatos.

### 2. Ejecución (Reaper)
Interfaz interactiva para borrar archivos confirmados.
- **Comando:** `python3 scripts/ghost_reaper.py --report ghost_report.json`
- **Modo:** Auditoría manual (y/n) para control total.

## Reglas de Limpieza
- **Entry Points:** Considera `main.py`, `index.ts`, `page.tsx`, etc., como raíces del grafo.
- **Assets:** Si una imagen no figura en ningún string del código, se marca como fantasma.
- **Seguridad:** Ignora `node_modules` y carpetas de sistema.
