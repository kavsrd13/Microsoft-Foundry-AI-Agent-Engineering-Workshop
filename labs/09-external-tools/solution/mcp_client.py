"""Lab 09, part 4 - Discover and call the tool over MCP.

Notice that we never told this client what tools exist. It asks.

Run it with:  python mcp_client.py
(mcp_server.py must be running in another terminal)
"""

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client("http://127.0.0.1:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n=== What tools does this server offer? ===")
            listing = await session.list_tools()
            for tool in listing.tools:
                print(f"  {tool.name}: {tool.description}")
                print(f"    arguments: {tool.inputSchema.get('properties', {})}")

            print("\n=== Calling one ===")
            result = await session.call_tool("get_order_status", {"order_id": "ORD-001"})
            for content in result.content:
                print(content.text)


if __name__ == "__main__":
    asyncio.run(main())
