"""
Agentic Reasoning Validator - Mermaid Visualizer
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Converts raw agent reasoning traces into professional Mermaid.js flowcharts,
             sequence diagrams, and state diagrams. Supports multiple visualization modes.
"""

import re
import json
from typing import List, Dict, Any, Optional
from enum import Enum


class VisualizationType(Enum):
    """Available visualization types."""
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    STATE = "state"
    JOURNEY = "journey"


class TraceVisualizer:
    """Professional Mermaid diagram generator for agent traces."""
    
    def __init__(self, trace_data: List[Dict[str, Any]], config: Optional[Dict] = None):
        self.trace_data = trace_data
        self.config = config or {}
        self.theme = self.config.get("theme", "default")
    
    def _sanitize(self, text: str, max_length: int = 50) -> str:
        """Sanitize text for Mermaid syntax."""
        if not text:
            return "N/A"
        text = re.sub(r'[^a-zA-Z0-9\s\-_.,]', '', text)
        text = text.strip()[:max_length]
        return text if text else "N/A"

    def _get_sanitized_label(self, text: str, max_length: int = 40) -> str:
        """Get properly sanitized label for Mermaid nodes."""
        if not text:
            return "N/A"
        text = re.sub(r'[\n\r]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        return text

    def generate_flowchart(self, loop_detection: Optional[Dict] = None) -> str:
        """Generate Mermaid flowchart from trace data."""
        lines = ["flowchart TD"]
        
        if self.theme == "dark":
            lines.append("    classDef default fill:#1e293b,stroke:#334155,color:#f1f5f9")
            lines.append("    classDef loop fill:#7f1d1d,stroke:#991b1b,color:#fecaca")
            lines.append("    classDef success fill:#14532d,stroke:#166534,color:#bbf7d0")
        else:
            lines.append("    classDef default fill:#f8fafc,stroke:#94a3b8,color:#1e293b")
            lines.append("    classDef loop fill:#fef2f2,stroke:#ef4444,color:#dc2626")
            lines.append("    classDef success fill:#f0fdf4,stroke:#22c55e,color:#16a34a")
        
        loop_positions = set()
        if loop_detection and loop_detection.get("loops"):
            for loop in loop_detection["loops"]:
                loop_positions.update(loop.get("positions", []))
        
        lines.append('    Start([<b>Start</b>])')
        
        for i, entry in enumerate(self.trace_data):
            step_id = i + 1
            thought = self._get_sanitized_label(entry.get("thought", f"Step {step_id}"))
            action = self._get_sanitized_label(entry.get("action", entry.get("tool", "No Action")))
            observation = self._get_sanitized_label(entry.get("observation", "No result"), 30)
            
            status = entry.get("status", "default")
            node_class = "default"
            if status in ["CRITICAL_LOOP", "POTENTIAL_LOOP"] or i in loop_positions:
                node_class = "loop"
            elif status in ["HEALTHY", "EXCELLENT"]:
                node_class = "success"
            
            lines.append(f'    S{step_id}["<b>Thought</b><br/>{thought}"]')
            lines.append(f'    S{step_id} ::: {node_class}')
            
            if action and action != "No Action":
                lines.append(f'    S{step_id} --> A{step_id}{{{{"<b>Action</b><br/>{action}}}}}')
                lines.append(f'    A{step_id} --> O{step_id}("<b>Result</b><br/>{observation}...")')
                
                if i < len(self.trace_data) - 1:
                    lines.append(f'    O{step_id} --> S{i+2}')
                else:
                    lines.append(f'    O{step_id} --> End([<b>End</b>])')
            else:
                if i < len(self.trace_data) - 1:
                    lines.append(f'    S{step_id} --> S{i+2}')
                else:
                    lines.append(f'    S{step_id} --> End([<b>End</b>])')
        
        return '\n'.join(lines)

    def generate_sequence(self) -> str:
        """Generate Mermaid sequence diagram."""
        lines = ["sequenceDiagram"]
        
        lines.append("    participant User")
        lines.append("    participant Agent")
        
        tools_seen = set()
        
        for i, entry in enumerate(self.trace_data):
            step_id = i + 1
            thought = self._get_sanitized_label(entry.get("thought", ""), 60)
            action = entry.get("action", entry.get("tool", ""))
            
            if thought:
                lines.append(f"    Note over Agent: Step {step_id}: {thought}")
            
            if action:
                tool_name = action.split('(')[0] if '(' in action else action
                
                if tool_name not in tools_seen:
                    lines.append(f"    participant {tool_name.title().replace('_', '')} as {tool_name}")
                    tools_seen.add(tool_name)
                
                lines.append(f"    Agent->>{tool_name.title().replace('_', '')}: {action}")
                
                observation = self._get_sanitized_label(entry.get("observation", "done"), 50)
                lines.append(f"    {tool_name.title().replace('_', '')}-->>Agent: {observation}")
        
        return '\n'.join(lines)

    def generate_state(self, entropy_data: Optional[List[Dict]] = None) -> str:
        """Generate Mermaid state diagram with health indicators."""
        lines = ["stateDiagram-v2"]
        lines.append("    [*] --> Initial")
        lines.append("    state Initial {")
        lines.append("        [*] --> Processing")
        lines.append("    }")
        
        for i, entry in enumerate(self.trace_data):
            status = "default"
            
            if entropy_data and i < len(entropy_data):
                status = entropy_data[i].get("status", "default")
            
            status_emoji = "⚪"
            if "HEALTHY" in status or "EXCELLENT" in status:
                status_emoji = "🟢"
            elif "POTENTIAL" in status:
                status_emoji = "🟡"
            elif "CRITICAL" in status:
                status_emoji = "🔴"
            
            lines.append(f"    Processing: Step {i+1} {status_emoji}")
        
        lines.append("    Processing --> [*]")
        
        return '\n'.join(lines)

    def generate_journey(self, entropy_data: Optional[List[Dict]] = None) -> str:
        """Generate Mermaid journey diagram showing agent's cognitive journey."""
        lines = ["journey"]
        lines.append("    title Agent Reasoning Journey")
        
        for i, entry in enumerate(self.trace_data):
            thought = self._get_sanitized_label(entry.get("thought", f"Step {i+1}"), 50)
            
            score = 5
            if entropy_data and i < len(entropy_data):
                entropy = entropy_data[i].get("entropy", 5)
                if entropy < 2:
                    score = 1
                elif entropy < 3:
                    score = 2
                elif entropy < 4:
                    score = 3
                elif entropy < 5:
                    score = 4
            
            lines.append(f"    section Step {i+1}")
            lines.append(f"      {thought}: {score}: Agent")
        
        return '\n'.join(lines)

    def generate_mermaid(
        self, 
        viz_type: VisualizationType = VisualizationType.FLOWCHART,
        loop_detection: Optional[Dict] = None,
        entropy_data: Optional[List[Dict]] = None
    ) -> str:
        """Generate Mermaid diagram based on specified type."""
        if viz_type == VisualizationType.FLOWCHART:
            return self.generate_flowchart(loop_detection)
        elif viz_type == VisualizationType.SEQUENCE:
            return self.generate_sequence()
        elif viz_type == VisualizationType.STATE:
            return self.generate_state(entropy_data)
        elif viz_type == VisualizationType.JOURNEY:
            return self.generate_journey(entropy_data)
        
        return self.generate_flowchart(loop_detection)

    def generate_all(self, audit_result: Optional[Dict] = None) -> Dict[str, str]:
        """Generate all visualization types."""
        loop_detection = None
        entropy_data = None
        
        if audit_result:
            loop_detection = audit_result.get("detected_loops")
            entropy_data = audit_result.get("entropy_analysis")
        
        return {
            "flowchart": self.generate_mermaid(VisualizationType.FLOWCHART, loop_detection, entropy_data),
            "sequence": self.generate_mermaid(VisualizationType.SEQUENCE),
            "state": self.generate_mermaid(VisualizationType.STATE, loop_detection, entropy_data),
            "journey": self.generate_mermaid(VisualizationType.JOURNEY, loop_detection, entropy_data)
        }


if __name__ == "__main__":
    sample_trace = [
        {
            "thought": "Searching for flight data to Paris",
            "action": "search_flights(destination='Paris')",
            "observation": "Found 3 flights, prices range $400-$800"
        },
        {
            "thought": "Filtering by price to find cheapest option",
            "action": "filter_flights(price_max=500)",
            "observation": "Found 2 flights under $500"
        },
        {
            "thought": "Verifying the data looks consistent",
            "action": "get_flight_details(flight_id=2)",
            "observation": "Confirmed: Flight 2 is $450, direct route"
        }
    ]
    
    viz = TraceVisualizer(sample_trace, {"theme": "default"})
    
    print("=" * 60)
    print("FLOWCHART:")
    print("=" * 60)
    print(viz.generate_mermaid(VisualizationType.FLOWCHART))
    
    print("\n" + "=" * 60)
    print("SEQUENCE DIAGRAM:")
    print("=" * 60)
    print(viz.generate_mermaid(VisualizationType.SEQUENCE))
