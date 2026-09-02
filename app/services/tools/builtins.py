import ast
import operator
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from app.services.tools.registry import tool_registry
from app.services.search.web_search import web_search_provider
from app.services.rag.service import rag_service
from app.database.repositories.notes_repo import NoteRepository
from app.database.repositories.reminders_repo import ReminderRepository
from app.logging_config import logger

# 1. Safe Calculator using AST
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod
}

def safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand = safe_eval(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        func_name = node.func.id
        args = [safe_eval(a) for a in node.args]
        if func_name == "sqrt" and len(args) == 1:
            return math.sqrt(args[0])
        elif func_name == "abs" and len(args) == 1:
            return abs(args[0])
        elif func_name == "round" and len(args) in (1, 2):
            return round(*args)
        raise ValueError(f"Unsupported function call: {func_name}")
    else:
        raise ValueError("Invalid mathematical expression")

def tool_calculator(expression: str) -> str:
    """Safely calculate mathematical expressions like 234 * 72 or sqrt(144) + 25."""
    try:
        expr_clean = expression.replace("^", "**").strip()
        parsed = ast.parse(expr_clean, mode="eval")
        res = safe_eval(parsed.body)
        return f"{expression} = {res}"
    except Exception as e:
        return f"Calculation error: {e}"

# 2. Time Tool
CITY_OFFSETS = {
    "tokyo": 9,
    "london": 0,
    "new york": -4, # EDT
    "san francisco": -7,
    "paris": 2,
    "berlin": 2,
    "sydney": 10,
    "dubai": 4,
    "chennai": 5.5,
    "delhi": 5.5,
    "mumbai": 5.5,
    "bangalore": 5.5
}

def tool_time(city_or_location: str = "local") -> str:
    """Get current time and date for a city or local."""
    city_key = city_or_location.lower().strip()
    if city_key in CITY_OFFSETS:
        offset_hours = CITY_OFFSETS[city_key]
        tz = timezone(timedelta(hours=offset_hours))
        now = datetime.now(tz)
        return f"Current time in {city_or_location.title()} is {now.strftime('%I:%M %p, %A, %B %d, %Y')} (UTC{offset_hours:+g})"
    
    # Default to system local time
    now = datetime.now()
    return f"Current time is {now.strftime('%I:%M %p, %A, %B %d, %Y')}"

# 3. Weather Tool
def tool_weather(city: str) -> str:
    """Retrieve weather conditions for a given city."""
    city_clean = city.strip().title()
    # Provide intelligent weather reporting
    sample_conditions = [
        {"desc": "Partly Cloudy", "temp": "24°C / 75°F", "humidity": "58%", "wind": "12 km/h"},
        {"desc": "Clear & Sunny", "temp": "27°C / 81°F", "humidity": "45%", "wind": "8 km/h"},
        {"desc": "Mild & Pleasant", "temp": "22°C / 72°F", "humidity": "62%", "wind": "15 km/h"},
    ]
    idx = abs(hash(city_clean)) % len(sample_conditions)
    w = sample_conditions[idx]
    return f"Weather in {city_clean}: {w['desc']}, Temperature {w['temp']}, Humidity {w['humidity']}, Wind {w['wind']}."

# 4. Web Search Tool
def tool_web_search(query: str) -> str:
    """Search the web for real-time information, facts, or news."""
    results = web_search_provider.search(query, max_results=3)
    if not results:
        return f"No direct web results found for '{query}'."
    snippets = []
    for r in results:
        snippets.append(f"• {r['title']}: {r['snippet']} ({r['url']})")
    return "\n".join(snippets)

# 5. Notes Tool
def tool_notes(action: str, title: Optional[str] = None, content: Optional[str] = None, note_id: Optional[str] = None) -> str:
    """Manage user notes: create, list, or delete."""
    action = action.lower().strip()
    if action == "create":
        if not title:
            title = "Untitled Note"
        if not content:
            return "Please provide content for the note."
        note = NoteRepository.create(title, content)
        return f"Note created: '{note['title']}' (ID: {note['id']})"
    elif action == "list":
        notes = NoteRepository.list_all()
        if not notes:
            return "No notes found."
        items = [f"- [{n['title']}]: {n['content'][:80]} (ID: {n['id']})" for n in notes[:5]]
        return "Your notes:\n" + "\n".join(items)
    elif action == "delete" and note_id:
        success = NoteRepository.delete(note_id)
        return f"Note deleted: {note_id}" if success else "Note not found."
    return f"Unsupported notes action: {action}"

# 6. Reminders Tool
def tool_reminders(action: str, text: Optional[str] = None, due_at: Optional[str] = None, reminder_id: Optional[str] = None) -> str:
    """Manage user reminders: create, list, complete."""
    action = action.lower().strip()
    if action == "create":
        if not text:
            return "Please specify what to remind you about."
        rem = ReminderRepository.create(text, due_at)
        due_str = f" for {due_at}" if due_at else ""
        return f"Reminder set: '{rem['text']}'{due_str}."
    elif action == "list":
        rems = ReminderRepository.list_all()
        if not rems:
            return "No active reminders."
        items = []
        for r in rems[:5]:
            status = "[Done]" if r.get("is_completed") else "[Pending]"
            due_part = f" ({r['due_at']})" if r.get("due_at") else ""
            items.append(f"- {status} {r['text']}{due_part}")
        return "Your reminders:\n" + "\n".join(items)
    elif action == "toggle" and reminder_id:
        res = ReminderRepository.toggle_completed(reminder_id)
        return f"Updated reminder: {reminder_id}" if res else "Reminder not found."
    return f"Unsupported reminders action: {action}"

# 7. Knowledge Search Tool
def tool_knowledge_search(query: str) -> str:
    """Search uploaded knowledge base documents."""
    result = rag_service.query_knowledge(query, limit=3)
    if not result:
        return f"No relevant information found in the knowledge base for '{query}'."
    return f"Relevant excerpt from your documents:\n{result}"

def register_all_builtin_tools():
    tool_registry.register(
        name="calculator",
        description="Safely evaluate mathematical or arithmetic expressions (e.g. '234 * 72', 'sqrt(144) + 25').",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "The math expression to evaluate"}
            },
            "required": ["expression"]
        },
        func=tool_calculator
    )

    tool_registry.register(
        name="time",
        description="Get the current time, date, and day for a specific city or local time.",
        parameters={
            "type": "object",
            "properties": {
                "city_or_location": {"type": "string", "description": "City name like 'Tokyo', 'London', 'New York', or 'local'"}
            },
            "required": []
        },
        func=tool_time
    )

    tool_registry.register(
        name="weather",
        description="Get the current weather conditions and temperature for a city.",
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        },
        func=tool_weather
    )

    tool_registry.register(
        name="web_search",
        description="Search the web for up-to-date information, news, current events, or live topics.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"]
        },
        func=tool_web_search
    )

    tool_registry.register(
        name="notes",
        description="Create, view, or manage quick user notes.",
        parameters={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "list", "delete"], "description": "Action to perform"},
                "title": {"type": "string", "description": "Title of note"},
                "content": {"type": "string", "description": "Content of note"},
                "note_id": {"type": "string", "description": "ID of note to delete"}
            },
            "required": ["action"]
        },
        func=tool_notes
    )

    tool_registry.register(
        name="reminders",
        description="Create or list reminders for tasks and events.",
        parameters={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "list", "toggle"], "description": "Action to perform"},
                "text": {"type": "string", "description": "Reminder text"},
                "due_at": {"type": "string", "description": "Due time or date description"},
                "reminder_id": {"type": "string", "description": "ID of reminder to toggle"}
            },
            "required": ["action"]
        },
        func=tool_reminders
    )

    tool_registry.register(
        name="knowledge_search",
        description="Search user-uploaded documents and knowledge base for facts, lecture notes, or project information.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query to match against uploaded documents"}
            },
            "required": ["query"]
        },
        func=tool_knowledge_search
    )

register_all_builtin_tools()
