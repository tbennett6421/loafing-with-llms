import json
import inspect
from typing import Callable, Dict, Any
from ollama import chat

MODEL = 'llama3.1'
DEBUG = True

# === Tool Registry ===
tool_registry: Dict[str, Dict[str, Any]] = {}
tool_functions: Dict[str, Callable] = {}

def tool(description: str = ""):
    def decorator(fn: Callable):
        sig = inspect.signature(fn)
        params = sig.parameters

        # Build OpenAPI-style parameters schema
        param_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        for name, param in params.items():
            annotation = param.annotation
            param_type = "string"  # default fallback

            if annotation == int:
                param_type = "integer"
            elif annotation == float:
                param_type = "number"
            elif annotation == bool:
                param_type = "boolean"
            elif annotation == str:
                param_type = "string"

            param_schema["properties"][name] = {"type": param_type}
            if param.default is inspect.Parameter.empty:
                param_schema["required"].append(name)

        # Add tool to registry
        tool_registry[fn.__name__] = {
            "type": "function",
            "function": {
                "name": fn.__name__,
                "description": description or fn.__doc__ or "",
                "parameters": param_schema
            }
        }

        tool_functions[fn.__name__] = fn
        return fn
    return decorator

# === Tool Functions ===
@tool(description="Add two numbers together")
def add_two_numbers(a: float, b: float) -> float:
    return a + b

@tool(description="Subtract the second number from the first")
def subtract_two_numbers(a: float, b: float) -> float:
    return a - b

# === Debugging Helper ===
def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def parse_tool_args(args):
    if isinstance(args, str):
        return json.loads(args)
    return args

def handle_tool_call(tool_call):
    tool_name = tool_call["function"]["name"]
    raw_args = parse_tool_args(tool_call["function"]["arguments"])

    if tool_name not in tool_functions:
        raise ValueError(f"Unknown tool requested: {tool_name}")

    fn = tool_functions[tool_name]
    sig = inspect.signature(fn)
    coerced_args = {}

    for name, param in sig.parameters.items():
        expected_type = param.annotation
        value = raw_args.get(name)

        if expected_type in [int, float, str, bool] and value is not None:
            try:
                coerced_args[name] = expected_type(value)
            except Exception as e:
                raise TypeError(f"Failed to coerce argument '{name}' to {expected_type}: {e}")
        else:
            coerced_args[name] = value

    debug_print(f"\n[Model requested tool call: {tool_name} with args {coerced_args}]")
    result = fn(**coerced_args)
    debug_print(f"[Tool result: {result}]")

    assistant_msg = {
        "role": "assistant",
        "tool_calls": [tool_call]
    }

    tool_msg = {
        "role": "tool",
        "name": tool_name,
        "content": str(result),
    }

    if "id" in tool_call:
        tool_msg["tool_call_id"] = tool_call["id"]
    elif "function_call_id" in tool_call:
        tool_msg["tool_call_id"] = tool_call["function_call_id"]

    return assistant_msg, tool_msg

# === Conversation Loop ===
def run_conversation(user_input):
    messages = [
        {
            "role": "system",
            "content": (
                "You have access to some functions like add_two_numbers(a, b) and subtract_two_numbers(a, b). "
                "Use them to answer questions requiring math operations."
            )
        },
        {"role": "user", "content": user_input}
    ]

    # First model call with tools
    response = chat(
        model=MODEL,
        messages=messages,
        tools=list(tool_registry.values())
    )

    debug_print("\n[Initial response JSON]")
    debug_print(json.dumps(response, indent=2))

    tool_calls = response["message"].get("tool_calls", [])

    if not tool_calls:
        debug_print("\n[No tool calls from model]")
        print(f"\n🧠 Model Response: {response['message']['content']}")
        return

    # Process all tool calls
    for tool_call in tool_calls:
        assistant_msg, tool_msg = handle_tool_call(tool_call)
        messages.append(assistant_msg)
        messages.append(tool_msg)

    # Send back to model for final answer
    final_response = chat(
        model=MODEL,
        messages=messages
    )

    debug_print("\n[Final response JSON]")
    debug_print(json.dumps(final_response, indent=2))

    print(f"\n✅ Answer: {final_response['message']['content']}")

# === Run ===
if __name__ == "__main__":
    run_conversation("What is 9.5 minus 4?")
