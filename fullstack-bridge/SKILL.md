---
name: fullstack-bridge
description: Sincronizador de endpoints front-back. Detecta y repara desconexiones (404, 500, mismatch de esquemas). Usar cuando el front no habla con el back o hay que integrar features nuevas.
---

# Fullstack Bridge (Silogismo)

Lógica para arreglar la integración front-back. Automatiza el escaneo de rutas y la creación de handlers.

## Instalación rápida (CLI)

Para bajar la última versión desde el repo:
```bash
npx skills add https://github.com/joaquinescalante23/toolbox --skill fullstack-bridge
```

## Workflow

### 1. Escaneo (Análisis de Integridad)
- **Comando:** `python3 scripts/bridge_scanner.py --fe app/ --be api/` (ajustar rutas según Silogismo).
- **Qué busca:**
    - `broken_frontend`: Llamadas fetch/axios que el back no tiene.
    - `orphan_backend`: Rutas que no se usan.
    - `schema_drift`: Campos en el front que no coinciden con el DTO del back.

### 2. Soldadura (Solder)
Para cada error en `bridge_report.json`, aplicar los parches:

#### A. Falta el Controller (BE)
1. Extrae el payload que el front intenta mandar.
2. Inyecta el decorador `@app.get` o `@app.post` en el archivo de rutas de FastAPI.
3. Genera el placeholder con los campos que el componente necesita.

#### B. Ruta rota (Mismatch)
1. Si `/api/user` cambió a `/api/users`, actualiza todos los componentes de Next.js.
2. Sincroniza nombres de variables dinámicas (id vs userId).

#### C. Sincronización de Tipos
1. Actualiza `interfaces.ts` basándose en la respuesta real del backend.

## Notas Técnicas
- **Source of Truth:** El Backend manda.
- **Validación:** No se da por cerrado sin correr `tsc`.
- **Regla de oro:** Siempre mostrar el diff antes de escribir en disco.
