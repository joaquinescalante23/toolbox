import os
import re
import json
import ast
import argparse
from pathlib import Path

def detect_frameworks(fe_path, be_path):
    be_fw = "FastAPI" if any("fastapi" in f.read_text(errors='ignore').lower() for f in Path(be_path).rglob("*.py") if f.is_file()) else "Express"
    fe_fw = "Next.js" if any("next" in f.name.lower() for f in Path(fe_path).rglob("*") if f.is_file()) else "React"
    return fe_fw, be_fw

def scan_be(be_path, fw):
    endpoints = {}
    if fw == "FastAPI":
        for py_file in Path(be_path).rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(errors='ignore'))
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for dec in node.decorator_list:
                            if isinstance(dec, ast.Call) and hasattr(dec.func, 'attr'):
                                if dec.func.attr in ['get', 'post', 'put', 'delete'] and dec.args:
                                    route = dec.args[0].value if isinstance(dec.args[0], ast.Constant) else None
                                    if route:
                                        endpoints[route] = {"method": dec.func.attr.upper(), "file": str(py_file)}
            except: continue
    else:
        pattern = r'\.(get|post|put|delete)\s*\(\s*[\'"`](.*?)[\'"`]'
        for f in Path(be_path).rglob("*.[jt]s"):
            content = f.read_text(errors='ignore')
            for m in re.finditer(pattern, content):
                endpoints[m.group(2)] = {"method": m.group(1).upper(), "file": str(f)}
    return endpoints

def scan_fe(fe_path):
    calls = []
    pattern = r'(?:const|let|var)\s*\{(.*?)\}.*?(?:fetch|axios.*?)\s*\(\s*[`\'"](.*?)[`\'"]'
    for f in Path(fe_path).rglob("*.[jt]sx"):
        content = f.read_text(errors='ignore')
        for m in re.finditer(pattern, content, re.DOTALL):
            calls.append({
                "route": m.group(2),
                "file": str(f),
                "fields": [field.strip() for field in m.group(1).split(',')]
            })
    return calls

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fe", required=True)
    parser.add_argument("--be", required=True)
    args = parser.parse_args()

    fe_fw, be_fw = detect_frameworks(args.fe, args.be)
    be_data = scan_be(args.be, be_fw)
    fe_data = scan_fe(args.fe)

    report = {"frameworks": {"fe": fe_fw, "be": be_fw}, "issues": []}

    for call in fe_data:
        route = call["route"]
        clean_route = re.sub(r'\$\{.*?\}|:.*?(?=/|$)', '*', route)
        match = next((be_data[r] for r in be_data if re.sub(r'\{.*?\}|:.*?(?=/|$)', '*', r) == clean_route), None)
        
        if not match:
            report["issues"].append({
                "type": "404_MISSING_BACKEND",
                "route": route,
                "file": call["file"],
                "fields": call["fields"]
            })

    with open("bridge_report.json", "w") as f:
        json.dump(report, f, indent=4)
    print(f"Audit completo. Frameworks: {fe_fw}/{be_fw}. Issues: {len(report['issues'])}")

if __name__ == "__main__":
    main()
