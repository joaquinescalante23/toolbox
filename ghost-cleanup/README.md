# ghost-cleanup

Limpieza quirúrgica de deuda técnica. Detecta archivos y assets que nadie usa mediante análisis de Grafo de Referencias Estático (STG).

## Problemas que resuelve
- **Archivos Fantasma:** Código que ya no se importa en ningún lado.
- **Assets Huérfanos:** Imágenes, fuentes y archivos pesados que no figuran en el código.
- **Zombie Exports:** Funciones exportadas que no tienen consumidores.

## Instalación

```bash
npx skills add https://github.com/joaquinescalante23/toolbox --skill ghost-cleanup
```

## Uso

1. **Auditoría:** `python3 scripts/ghost_scanner.py --root <path_proyecto>`
2. **Eliminación:** `python3 scripts/ghost_reaper.py --report ghost_report.json`

## Arquitectura
- **Root-Trace:** Rastreo de imports desde los entry points (`index`, `main`, `page`).
- **Asset Matcher:** Cruce de nombres de archivos contra el contenido del código.
- **Modo Auditoría:** Interfaz interactiva (y/n) para evitar borrados accidentales.
