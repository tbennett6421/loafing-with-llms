from praisonaiagents import Agent, MCP

# LLM choices: llama3.2 (3B), falcon3 (3B), falcon3:7b (7B)

single_tool_agent = Agent(
    instructions=(
        "You are a helpful assistant. "
        "When the user asks for a favicon, call the tool `get_favicon_hash` "
        "with a single argument: the clean base URL (scheme + domain only). "
        "Do not include any extra text in the argument."
    ),
    llm="ollama/qwen3",
    tools=MCP("python src/servers/favicon.py")
)


print("🔧 Agent initialized. You can now chat with it (type 'exit' to quit).")
print("--------------------------------------------------------------")

# Interactive loop
while True:
    try:
        user_input = input("🧑 You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting chat.")
            break
        response = single_tool_agent.start(user_input)
        print(f"🤖 Agent: {response}\n")
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Exiting chat.")
        break
    except Exception as e:
        print(f"⚠️ Error: {e}")
