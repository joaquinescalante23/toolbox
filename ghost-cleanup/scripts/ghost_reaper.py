import json
import os
import argparse
from pathlib import Path

def reaper(report_path):
    with open(report_path, 'r') as f:
        data = json.load(f)
    
    root = Path(data["root"])
    ghosts = data["ghosts"]
    
    print(f"\n--- 💀 REAPER MODE: Auditoría de {len(ghosts)} archivos ---\n")
    
    deleted_count = 0
    for ghost in ghosts:
        path = root / ghost
        if not path.exists():
            continue
            
        choice = input(f"¿Borrar {ghost}? (y/n): ").lower()
        if choice == 'y':
            try:
                path.unlink()
                print(f"✅ Eliminado: {ghost}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error al borrar {ghost}: {e}")
        else:
            print(f"⏭️  Omitido: {ghost}")
            
    print(f"\nLimpieza finalizada. Archivos eliminados: {deleted_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="ghost_report.json")
    args = parser.parse_args()
    
    if os.path.exists(args.report):
        reaper(args.report)
    else:
        print("No se encontró el reporte de fantasmas.")
