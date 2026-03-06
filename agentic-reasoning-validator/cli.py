#!/usr/bin/env python3
"""
Agentic Reasoning Validator - CLI Orchestrator
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Professional CLI for auditing agent reasoning traces.
"""

import sys
import json
import argparse
from pathlib import Path
from scripts.trace_parser import TraceParser
from scripts.semantic_auditor import SemanticAuditor
from scripts.trace_to_mermaid import TraceVisualizer, VisualizationType


def run_full_audit(
    raw_log_path: str, 
    output_path: str = "audit_report.json",
    visualize: bool = True,
    tool_schema: list = None
):
    """Run a complete audit on an agent trace log."""
    print(f"🚀 Initializing Audit for: {raw_log_path}")
    
    log_path = Path(raw_log_path)
    if not log_path.exists():
        print(f"❌ Error: File '{raw_log_path}' not found.")
        sys.exit(1)
    
    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()
    
    print("📋 Parsing trace...")
    parser = TraceParser(log_content)
    structured_data = parser.get_structured_trace()
    
    print(f"   Detected format: {structured_data.get('detected_format', 'unknown')}")
    
    thoughts = []
    for entry in structured_data.get('structured_trace', []):
        if 'thought' in entry and entry['thought']:
            thoughts.append(entry['thought'])
    
    if not thoughts and log_content:
        thoughts = [log_content]
    
    print(f"   Extracted {len(thoughts)} thought entries")
    
    print("🔍 Running semantic analysis...")
    auditor = SemanticAuditor(thoughts, tool_schema=tool_schema)
    audit_report = auditor.audit_drift()
    
    print(f"   Health Score: {audit_report.get('health_score', 0)}/100 ({audit_report.get('overall_health', 'UNKNOWN')})")
    
    if audit_report.get('circular_patterns'):
        print(f"   ⚠️  Detected {len(audit_report['circular_patterns'])} circular pattern(s)")
    if audit_report.get('indecision_patterns'):
        print(f"   ⚠️  Found {len(audit_report['indecision_patterns'])} indecision marker(s)")
    
    viz_mermaid = None
    if visualize and structured_data.get('structured_trace'):
        print("🎨 Generating visualizations...")
        viz = TraceVisualizer(structured_data['structured_trace'])
        
        try:
            viz_mermaid = {
                "flowchart": viz.generate_mermaid(VisualizationType.FLOWCHART),
                "sequence": viz.generate_mermaid(VisualizationType.SEQUENCE),
                "state": viz.generate_mermaid(VisualizationType.STATE),
                "journey": viz.generate_mermaid(VisualizationType.JOURNEY)
            }
        except Exception as e:
            print(f"   ⚠️  Visualization error: {e}")
            viz_mermaid = {"flowchart": viz.generate_mermaid(VisualizationType.FLOWCHART)}
    
    final_report = {
        "metadata": {
            "author": "joaquinescalante23",
            "version": "2.0.0-PRO",
            "source_file": str(raw_log_path)
        },
        "parsing": {
            "detected_format": structured_data.get('detected_format'),
            "metadata": structured_data.get('metadata'),
            "loops_detected": structured_data.get('detected_loops', {})
        },
        "audit": audit_report,
        "recommendations": auditor.generate_recommendations(),
        "visualization": viz_mermaid
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Audit Complete!")
    print(f"   Report saved to: {output_path}")
    print(f"   Health: {audit_report.get('overall_health', 'UNKNOWN')} ({audit_report.get('health_score', 0)}/100)")
    
    if visualize and viz_mermaid:
        print(f"\n📊 To visualize, copy the flowchart to: https://mermaid.live/")
        print("\n--- Mermaid Flowchart Preview ---")
        print(viz_mermaid.get("flowchart", "N/A")[:500] + "...")


def main():
    parser = argparse.ArgumentParser(
        description="Agentic Reasoning Validator - Audit and visualize agent reasoning traces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s logs/agent_trace.txt
  %(prog)s logs/agent_trace.txt -o my_report.json
  %(prog)s logs/agent_trace.txt --no-viz
  %(prog)s logs/agent_trace.txt --tools get_weather search_flights filter_flights
        """
    )
    
    parser.add_argument(
        "input_file", 
        help="Path to the agent trace log file"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="audit_report.json",
        help="Output report path (default: audit_report.json)"
    )
    
    parser.add_argument(
        "--no-viz", "--no-visualization",
        action="store_true",
        help="Skip Mermaid visualization generation"
    )
    
    parser.add_argument(
        "--tools",
        nargs="*",
        help="List of valid tool names for hallucination detection"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    run_full_audit(
        args.input_file,
        output_path=args.output,
        visualize=not args.no_viz,
        tool_schema=args.tools
    )


if __name__ == "__main__":
    main()
