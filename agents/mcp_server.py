# mcp_client.py
import asyncio
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent

async def main():
    client = BasicMCPClient("http://localhost:8000/sse")  # or stdio
    tools = await McpToolSpec(client=client).to_tool_list_async()

    llm = Ollama(model="llama3.1")
    agent = FunctionAgent(tools=tools, llm=llm,
                          system_prompt="You can query the local document index using provided tools.")

    resp = await agent.run("Explain how to set up a local MCP server with LlamaIndex.")
    print(resp)

if __name__ == "__main__":
    asyncio.run(main())