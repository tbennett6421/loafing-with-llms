import json
from ollama import chat

# Use a model that supports tools
MODEL = 'llama3.1'
DEBUG = True

# === Tool Functions ===
def add_two_numbers(a: float, b: float) -> float:
    return a + b

def subtract_two_numbers(a: float, b: float) -> float:
    return a - b

# === Tool Specs ===
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_two_numbers",
            "description": "Add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "subtract_two_numbers",
            "description": "Subtract the second number from the first",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"]
            }
        }
    }
]

# === Tool Dispatcher ===
tool_functions = {
    "add_two_numbers": add_two_numbers,
    "subtract_two_numbers": subtract_two_numbers,
}

# === Helpers ===
def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def parse_tool_args(args):
    if isinstance(args, str):
        return json.loads(args)
    return args

def handle_tool_call(tool_call):
    tool_name = tool_call["function"]["name"]
    args = parse_tool_args(tool_call["function"]["arguments"])
    debug_print(f"\n[Model requested tool call: {tool_name} with args {args}]")

    if tool_name not in tool_functions:
        raise ValueError(f"Unknown tool requested: {tool_name}")

    result = tool_functions[tool_name](**args)
    debug_print(f"[Tool result: {result}]")

    # Return the assistant's tool call message and the tool's response message
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

def run_conversation(user_input):
    messages = [
        {
            "role": "system",
            "content": (
                "You have access to two functions: add_two_numbers(a, b) and subtract_two_numbers(a, b). "
                "Use them to answer questions requiring math operations."
            )
        },
        {"role": "user", "content": user_input}
    ]

    # First model call with tools
    response = chat(
        model=MODEL,
        messages=messages,
        tools=tools
    )

    debug_print("\n[Initial response JSON]")
    debug_print(json.dumps(response, indent=2))

    tool_calls = response["message"].get("tool_calls", [])

    if not tool_calls:
        debug_print("\n[No tool calls from model]")
        print(f"\n🧠 Model Response: {response['message']['content']}")
        return

    # Process all tool calls and collect messages
    for tool_call in tool_calls:
        assistant_msg, tool_msg = handle_tool_call(tool_call)
        messages.append(assistant_msg)
        messages.append(tool_msg)

    # Send final message to model with tool results
    final_response = chat(
        model=MODEL,
        messages=messages
    )

    debug_print("\n[Final response JSON]")
    debug_print(json.dumps(final_response, indent=2))

    print(f"\n✅ Answer: {final_response['message']['content']}")

# === Run ===

if __name__ == "__main__":
    run_conversation("What is three plus one?")

