#!/usr/bin/env python3
"""Phase 5 - agent.py: Hand-built agent loop from scratch"""

import json
import os
import sys
from datetime import datetime

# Add phase5 to path for imports
sys.path.insert(0, os.path.dirname(__file__))

WORKSPACE = os.path.join(os.path.dirname(__file__), "workspace")
os.makedirs(WORKSPACE, exist_ok=True)

from tracker import tracked_call

# --- TOOLS ---

def read_file(path: str) -> str:
    """Read a file from the workspace folder only."""
    safe_path = os.path.join(WORKSPACE, os.path.basename(path))
    if not os.path.exists(safe_path):
        return json.dumps({"error": f"File not found: {path}"})
    with open(safe_path) as f:
        return json.dumps({"content": f.read()})

def search_docs(query: str) -> str:
    """Search the Phase 4 RAG index."""
    try:
        import sys
        sys.path.insert(0, "phase4")
        from ask import rag_answer_with_guardrail
        result = rag_answer_with_guardrail(query)
        return json.dumps({"answer": result["answer"], "sources": result["sources"]})
    except Exception as e:
        return json.dumps({"error": str(e)})

def calculator(expr: str) -> str:
    """Safely evaluate a math expression."""
    try:
        allowed = set("0123456789+-*/()., ")
        if not all(c in allowed for c in expr):
            return json.dumps({"error": "Invalid characters in expression"})
        result = eval(expr, {"__builtins__": {}})
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})

def remember(note: str) -> str:
    """Write a note to the agent's persistent memory file."""
    notes_file = os.path.join(WORKSPACE, "agent_notes.txt")
    with open(notes_file, "a") as f:
        from datetime import datetime
        f.write(f"[{datetime.now().isoformat()}] {note}\n")
    return json.dumps({"status": "noted", "note": note})

def recall() -> str:
    """Read all notes from the agent's memory file."""
    notes_file = os.path.join(WORKSPACE, "agent_notes.txt")
    if not os.path.exists(notes_file):
        return json.dumps({"notes": "No notes yet."})
    with open(notes_file) as f:
        return json.dumps({"notes": f.read()})

TOOL_MAP = {
    "read_file": read_file,
    "search_docs": search_docs,
    "calculator": calculator,
    "remember": remember,
    "recall": recall
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the workspace. Use when you need to access a specific file.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Filename to read"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search the document knowledge base for information. Use when you need to answer questions from the business documents.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a math expression. Use for any arithmetic calculation.",
            "parameters": {
                "type": "object",
                "properties": {"expr": {"type": "string", "description": "Math expression, e.g. '45.99 * 1.1'"}},
                "required": ["expr"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Write a note to the agent's persistent memory. Used for long-term recall across sessions.",
            "parameters": {
                "type": "object",
                "properties": {"note": {"type": "string", "description": "Note to remember"}},
                "required": ["note"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recall",
            "description": "Read all notes from the agent's persistent memory. Used to retrieve previously saved information.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

SYSTEM_PROMPT = """You are a business assistant with access to tools.
Use tools to gather information before answering.
Never invent data — if you don't know, use search_docs or read_file.
When you have enough information, give a plain final answer.
Do not call tools unnecessarily.
Rules:
- Use read_file to access files in the workspace only
- Use search_docs to find information from your document knowledge base
- Use calculator for any arithmetic operations
- Use remember to save important information for later recall
- Never invent prices, dates, or order details
- Stop when you have a complete answer with all required information
- Give a plain final answer with no tool calls after you have enough information"""

def run_agent(task: str, max_steps: int = 8) -> dict:
    """Run the agent loop on a given task."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task}
    ]
    total_cost = 0.0
    steps_taken = 0

    for step in range(max_steps):
        steps_taken += 1
        result = tracked_call(messages, tools=tools)
        total_cost += result["cost"]

        if result["finish_reason"] == "stop":
            return {
                "success": True, 
                "answer": result["content"],
                "steps": steps_taken, 
                "cost": total_cost
            }

        if result["finish_reason"] in ("length", "content_filter"):
            return {
                "success": False, 
                "answer": None,
                "error": f"finish_reason={result['finish_reason']}",
                "steps": steps_taken, 
                "cost": total_cost
            }

        if result["finish_reason"] == "tool_calls":
            if result["message"]:
                messages.append(result["message"].model_dump() if hasattr(result["message"], 'model_dump') else result["message"])
            for tc in result["tool_calls"]:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                print(f"  Step {step+1}: {fn_name}({fn_args})")
                tool_result = TOOL_MAP.get(fn_name, lambda **_: json.dumps({"error": f"Unknown tool: {fn_name}"}))(** fn_args)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": tool_result})

    return {
        "success": False, 
        "answer": None,
        "error": f"Max steps ({max_steps}) reached",
        "steps": steps_taken, 
        "cost": total_cost
    }

if __name__ == "__main__":
    # Create a test file in workspace
    with open(os.path.join(WORKSPACE, "products.txt"), "w") as f:
        f.write("Product: Blue Hoodie | SKU: HOODIE-BLU-L | Price: $45.99\n")
        f.write("Product: Red Mug | SKU: MUG-RED | Price: $12.00\n")

    task = "Read the products file and calculate the total cost of buying 3 Blue Hoodies and 2 Red Mugs."
    print(f"Task: {task}\n")
    result = run_agent(task)
    print(f"Answer: {result['answer']}")
    print(f"Steps: {result['steps']} | Cost: ${result['cost']:.6f}")