import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_mcp_tools():
    """
    Crée un client MCP et récupère les tools disponibles.
    """
    client = MultiServerMCPClient({
        "medical-tools": {
            "command": "python",
            "args": ["../../mcp_server/server.py"],
            "transport": "stdio",
        }
    })

    tools = await client.get_tools()
    return tools, client


def get_mcp_tools_sync():
    """
    Version synchrone pour les environnements non-async.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        tools, client = loop.run_until_complete(get_mcp_tools())
        return tools
    finally:
        loop.close()
