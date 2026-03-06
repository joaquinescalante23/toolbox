"""
Agentic Reasoning Validator - Trace Parser
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Professional utility to parse, clean, and structure agentic reasoning logs (traces)
             from various frameworks (LangChain, AutoGPT, OpenAI Assistants, custom).
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TraceFormat(Enum):
    """Supported trace formats."""
    JSON = "json"
    OPENAI = "openai"
    LANGCHAIN = "langchain"
    AUTOGPT = "autogpt"
    ANTHROPIC = "anthropic"
    GENERIC = "generic"


class TraceParser:
    """Professional trace parser for agent reasoning logs."""
    
    def __init__(self, raw_log: str, format_hint: Optional[TraceFormat] = None):
        self.raw_log = raw_log
        self.format_hint = format_hint
        self._detected_format: Optional[TraceFormat] = None

    def detect_format(self) -> TraceFormat:
        """Auto-detect the trace format based on patterns."""
        if self.format_hint:
            return self.format_hint
        
        if '"thought"' in self.raw_log.lower() or '"action"' in self.raw_log.lower():
            if '"tool_calls"' in self.raw_log:
                return TraceFormat.OPENAI
            return TraceFormat.LANGCHAIN
        
        if "thought:" in self.raw_log.lower() and "action:" in self.raw_log.lower():
            return TraceFormat.AUTOGPT
        
        if '"role"' in self.raw_log and '"content"' in self.raw_log:
            return TraceFormat.ANTHROPIC
        
        if self._has_json_objects():
            return TraceFormat.JSON
        
        return TraceFormat.GENERIC

    def _has_json_objects(self) -> bool:
        """Check if log contains JSON objects."""
        return bool(re.search(r'\{[\s\S]*\}', self.raw_log))

    def extract_json_blobs(self) -> List[Dict[str, Any]]:
        """Extract all JSON objects from text log using robust parsing."""
        blobs = []
        
        bracket_depth = 0
        start_pos = None
        
        for i, char in enumerate(self.raw_log):
            if char == '{':
                if bracket_depth == 0:
                    start_pos = i
                bracket_depth += 1
            elif char == '}':
                bracket_depth -= 1
                if bracket_depth == 0 and start_pos is not None:
                    json_str = self.raw_log[start_pos:i+1]
                    try:
                        blobs.append(json.loads(json_str))
                    except json.JSONDecodeError:
                        pass
                    start_pos = None
        
        return blobs

    def extract_langchain_trace(self) -> List[Dict[str, Any]]:
        """Extract LangChain-style traces with actions, observations, thoughts."""
        traces = []
        
        thought_pattern = r'(?:thought|Thought|THOUGHT)[:\s]+([^\n]+)'
        action_pattern = r'(?:action|Action|ACTION)[:\s]+([^\n]+)'
        observation_pattern = r'(?:observation|Observation|OBSERVATION)[:\s]+([^\n]+)'
        tool_pattern = r'(?:tool|Tool|TOOL)[:\s]+([^\n]+)'
        
        entries = re.split(r'(?:Step|STEP|---|\n\d+\.)', self.raw_log)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            trace_entry = {}
            
            thought_match = re.search(thought_pattern, entry)
            if thought_match:
                trace_entry["thought"] = thought_match.group(1).strip()
            
            action_match = re.search(action_pattern, entry)
            if action_match:
                trace_entry["action"] = action_match.group(1).strip()
            
            tool_match = re.search(tool_pattern, entry)
            if tool_match:
                trace_entry["tool"] = tool_match.group(1).strip()
            
            observation_match = re.search(observation_pattern, entry)
            if observation_match:
                trace_entry["observation"] = observation_match.group(1).strip()
            
            if trace_entry:
                traces.append(trace_entry)
        
        return traces

    def extract_autogpt_trace(self) -> List[Dict[str, Any]]:
        """Extract AutoGPT-style traces (Thought:, Observation:, etc.)."""
        traces = []
        
        lines = self.raw_log.split('\n')
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            
            thought_match = re.match(r'Thought:\s*(.+)', line)
            if thought_match:
                if current_entry:
                    traces.append(current_entry)
                current_entry = {"thought": thought_match.group(1)}
                continue
            
            action_match = re.match(r'Action:\s*(.+)', line)
            if action_match:
                current_entry["action"] = action_match.group(1)
                continue
            
            observation_match = re.match(r'Observation:\s*(.+)', line)
            if observation_match:
                current_entry["observation"] = observation_match.group(1)
                traces.append(current_entry)
                current_entry = {}
                continue
            
            result_match = re.match(r'Result:\s*(.+)', line)
            if result_match:
                current_entry["result"] = result_match.group(1)
        
        if current_entry:
            traces.append(current_entry)
        
        return traces

    def extract_openai_trace(self) -> List[Dict[str, Any]]:
        """Extract OpenAI Assistant-style traces with tool calls."""
        traces = []
        json_blobs = self.extract_json_blobs()
        
        for blob in json_blobs:
            if "tool_calls" in blob or "message" in blob:
                traces.append(blob)
        
        return traces

    def detect_loops(self, threshold: int = 3) -> Dict[str, Any]:
        """Detect repeated patterns indicating loops."""
        lines = [line.strip() for line in self.raw_log.split('\n') if line.strip()]
        
        if len(lines) < threshold:
            return {"detected": False, "loops": []}
        
        line_history: Dict[str, List[int]] = {}
        detected_loops = []
        
        for idx, line in enumerate(lines):
            normalized = re.sub(r'\s+', ' ', line.lower())
            
            if normalized not in line_history:
                line_history[normalized] = []
            line_history[normalized].append(idx)
            
            if len(line_history[normalized]) >= threshold:
                detected_loops.append({
                    "line_preview": line[:100],
                    "occurrences": len(line_history[normalized]),
                    "positions": line_history[normalized][-threshold:],
                    "severity": "HIGH" if len(line_history[normalized]) >= threshold + 2 else "MEDIUM"
                })
        
        tool_call_pattern = r'(\w+)\s*\([^)]*\)'
        tool_calls = re.findall(tool_call_pattern, self.raw_log)
        tool_history: Dict[str, List[int]] = {}
        
        for idx, call in enumerate(tool_calls):
            if call not in tool_history:
                tool_history[call] = []
            tool_history[call].append(idx)
            
            if len(tool_history[call]) >= threshold:
                detected_loops.append({
                    "type": "tool_loop",
                    "tool": call,
                    "occurrences": len(tool_history[call]),
                    "positions": tool_history[call][-threshold:],
                    "severity": "CRITICAL" if len(tool_history[call]) >= threshold + 2 else "HIGH"
                })
        
        return {
            "detected": len(detected_loops) > 0,
            "loops": detected_loops,
            "total_lines": len(lines),
            "unique_lines": len(line_history)
        }

    def extract_metadata(self) -> Dict[str, Any]:
        """Extract metadata from the trace."""
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "format": self.detect_format().value,
            "length_chars": len(self.raw_log),
            "length_lines": len(self.raw_log.split('\n')),
            "json_objects_found": len(self.extract_json_blobs())
        }
        
        tool_pattern = r'(\w+)\s*\('
        tools_found = re.findall(tool_pattern, self.raw_log)
        if tools_found:
            metadata["tools_used"] = list(set(tools_found))
            metadata["tool_call_count"] = len(tools_found)
        
        return metadata

    def get_structured_trace(self) -> Dict[str, Any]:
        """Returns a fully structured trace with all analyses."""
        self._detected_format = self.detect_format()
        
        if self._detected_format == TraceFormat.AUTOGPT:
            structured = self.extract_autogpt_trace()
        elif self._detected_format == TraceFormat.OPENAI:
            structured = self.extract_openai_trace()
        elif self._detected_format == TraceFormat.LANGCHAIN:
            structured = self.extract_langchain_trace()
        else:
            structured = self.extract_json_blobs()
        
        return {
            "metadata": self.extract_metadata(),
            "detected_format": self._detected_format.value,
            "detected_loops": self.detect_loops(),
            "structured_trace": structured,
            "status": "parsed"
        }

    def to_langchain_format(self) -> List[Dict[str, Any]]:
        """Convert trace to LangChain AgentExecutor format."""
        trace = self.get_structured_trace()
        langchain_steps = []
        
        for idx, entry in enumerate(trace.get("structured_trace", [])):
            step = {
                "step": idx,
                "action": entry.get("action", entry.get("tool", "unknown")),
                "observation": entry.get("observation", entry.get("result", "")),
                "thought": entry.get("thought", "")
            }
            langchain_steps.append(step)
        
        return langchain_steps


if __name__ == "__main__":
    sample_log = """
Thought: I need to check the weather in London.
Action: get_weather(city="London")
Observation: The weather is sunny, 22°C.

Thought: The weather is nice, let me check if I should bring sunglasses.
Action: get_uv_index(city="London")
Observation: UV index is 5, moderate.

Thought: I need to check the weather again to be sure.
Action: get_weather(city="London")
Observation: The weather is sunny, 22°C.

Thought: Let me verify the data one more time.
Action: get_weather(city="London")
Observation: The weather is sunny, 22°C.
    """
    
    parser = TraceParser(sample_log)
    result = parser.get_structured_trace()
    print(json.dumps(result, indent=2))
