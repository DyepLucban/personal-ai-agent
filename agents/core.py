from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain import chat_models
from config.settings import RUNNER_MODEL, RUNNER_MODEL_BASE_URL
from config.prompts import GENERAL_PURPOSE

def run_core(query: str, tools = []):
    max_iteration = 5
    tool_map = {t.name: t for t in tools}

    # Build message
    message = [
        SystemMessage(content=GENERAL_PURPOSE),
        HumanMessage(content=query)
    ]

    # Instantiate OpenAI
    llm = ChatOpenAI(
        model=RUNNER_MODEL,
        base_url=RUNNER_MODEL_BASE_URL,
        api_key="not-needed",
        temperature=0.5
    )

    # Attach tools
    llm_with_tools = llm.bind_tools(tools) if tools else llm

    for i in range(max_iteration):
        # Invoke chat
        response = llm_with_tools.invoke(message)

        # return response
        print(f"[ITERATION {i+1}]")
        message.append(response)

        # If no tools is being used, return original response
        if not response.tool_calls:
            print("NO TOOLS")
            return response.content

        # Loop to the tools
        for tc in response.tool_calls:
            tool_name = tc["name"]
            print(f"HAS TOOL(S): {tool_name}")
            tool_fn = tool_map.get(tool_name)
            
            if not tool_fn:
                message.append(ToolMessage(content=f"Unknown tool: {tool_name}", tool_call_id=tc["id"]))
                continue

            try:
                result = tool_fn.invoke(tc["args"])
                message.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
            except Exception as e:
                print(f"Error: {e}")
                message.append(ToolMessage(content=f"Error: {e}", tool_call_id=tc["id"]))

    # Fallback if loop exhausts without a final answer
    return "Sorry, I couldn't complete the request in time."

    