import os
import re
import json
import argparse
from pathlib import Path
from functools import lru_cache

# Optimización: Patrones pre-compilados
IMPORT_PATTERNS = [
    re.compile(r'import.*?from\s*[\'"`](.*?)[\'"`]'),
    re.compile(r'require\s*\(\s*[\'"`](.*?)[\'"`]'),
    re.compile(r'from\s+(.*?)\s+import'),
]

ASSET_EXTS = {'.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp', '.woff', '.woff2', '.mp4', '.pdf'}

@lru_cache(maxsize=1024)
def resolve_import(current_dir, import_path):
    if not import_path.startswith('.'):
        return None
    path = (Path(current_dir) / import_path).resolve()
    for ext in ['.ts', '.tsx', '.js', '.jsx', '.py']:
        if (path / f"index{ext}").exists(): return path / f"index{ext}"
        if path.with_suffix(ext).exists(): return path.with_suffix(ext)
    return path if path.exists() else None

def scan_project(root_path):
    root = Path(root_path).resolve()
    all_files = set()
    
    # Directorios a ignorar completamente
    IGNORE_DIRS = {'.git', '__pycache__', '.mypy_cache', '.next', '.venv', 'node_modules', '.DS_Store'}
    
    for f in root.rglob("*"):
        # Saltar si el archivo o cualquier parte de su ruta está en IGNORE_DIRS o empieza con punto
        if any(part in IGNORE_DIRS or (part.startswith('.') and part != '.') for part in f.parts):
            continue
            
        if f.is_file():
            all_files.add(f)

    # Cachear contenido de archivos de código
    code_contents = {}
    entry_points = []
    for f in all_files:
        if f.suffix in {'.ts', '.tsx', '.js', '.jsx', '.py'}:
            try:
                content = f.read_text(errors='ignore')
                code_contents[f] = content
                if f.name in ['main.py', 'index.ts', 'index.js', 'page.tsx']:
                    entry_points.append(f)
            except: continue

    reachable = set(entry_points)
    queue = list(entry_points)
    
    # Grafo de importación (Crawl)
    while queue:
        curr = queue.pop(0)
        content = code_contents.get(curr, "")
        for pattern in IMPORT_PATTERNS:
            for match in pattern.findall(content):
                resolved = resolve_import(curr.parent, match)
                if resolved and resolved not in reachable:
                    reachable.add(resolved)
                    queue.append(resolved)

    # Optimización: Búsqueda de assets por intersección de nombres
    # Para evitar O(n*m), creamos un set de todas las "palabras" en el código
    all_code_words = set()
    for content in code_contents.values():
        all_code_words.update(re.findall(r'[\w\-\.]+', content))

    for f in all_files:
        if f.suffix in ASSET_EXTS and f.name in all_code_words:
            reachable.add(f)

    ghosts = [str(f.relative_to(root)) for f in all_files if f not in reachable]
    return ghosts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    ghosts = scan_project(args.root)
    with open("ghost_report.json", "w") as f:
        json.dump({"root": args.root, "ghost_count": len(ghosts), "ghosts": ghosts}, f, indent=4)
    print(f"Audit finalizado. {len(ghosts)} archivos fantasmas detectados.")

if __name__ == "__main__":
    main()
