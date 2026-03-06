# fullstack-bridge

Sincronizador de integridad para aplicaciones Fullstack. Detecta y repara desconexiones entre el Frontend (Next.js/React) y el Backend (FastAPI/Express) mediante análisis estático y generación de código.

## Problemas que resuelve
- **404 Preventivos:** Detecta llamadas desde el front a rutas que no existen en el servidor.
- **Orphan Routes:** Identifica endpoints en el backend que no están siendo consumidos.
- **Schema Drift:** Encuentra desajustes entre los campos que el frontend desestructura y los que el backend envía realmente.

## Instalación

```bash
npx skills add https://github.com/joaquinescalante23/toolbox --skill fullstack-bridge
```

## Guía de Uso

### 1. Auditoría (Scanner)
El scanner analiza el AST (Abstract Syntax Tree) para mapear la infraestructura sin ejecutar el código.

```bash
python3 scripts/bridge_scanner.py --fe <path_al_front> --be <path_al_back>
```
Genera un archivo `bridge_report.json` con el estado de la conexión.

### 2. Reparación (Solderer)
El motor de "soldadura" toma el reporte y genera los parches necesarios.

```bash
python3 scripts/bridge_solderer.py --report bridge_report.json
```
- Si falta un endpoint, genera el controlador con el JSON de respuesta esperado.
- Si hay un cambio de ruta, sugiere el refactor en el cliente.

## Arquitectura
- **Discovery:** Análisis de decoradores en Python y métodos de ruteo en JS/TS.
- **Inferencia:** Rastreo de variables y desestructuración para determinar el contrato de datos (payloads).
- **Inyección:** Generación de código idiomático basado en el framework detectado (FastAPI, Express, Next.js).
