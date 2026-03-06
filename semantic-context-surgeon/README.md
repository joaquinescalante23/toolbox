# fullstack-bridge

Sincronización de endpoints front-back para Silogismo (o cualquier setup FastAPI/Next.js). Detecta y arregla 404s, 500s y desvíos de esquemas JSON.

## Instalación

```bash
npx skills add https://github.com/joaquinescalante23/fullstack-bridge
```

## Uso

1. **Escaneo:** `python3 scripts/bridge_scanner.py --fe <front> --be <api>`
2. **Reparación:** `python3 scripts/bridge_solderer.py --report bridge_report.json`

## Arquitectura
- Análisis de AST para rutas backend.
- Rastreo de desestructuración en el front para inferencia de payloads.
- Generación automática de controladores.
