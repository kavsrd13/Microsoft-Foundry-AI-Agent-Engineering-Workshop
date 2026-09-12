"""Lab 09, part 3 - Publish the tool over MCP.

MCP lets any MCP-speaking client discover and call your tool without you
writing a schema by hand. The docstring and type hints below become the
tool's description and its argument schema.

Run it with:  python mcp_server.py
Leave it running, then run mcp_client.py in another terminal.
"""

from mcp.server.fastmcp import FastMCP

from use_the_tool import call_the_tool

server = FastMCP("Acme orders", host="127.0.0.1", port=8000)


@server.tool()
def get_order_status(order_id: str) -> dict:
    """Look up one Acme order by its order ID, for example ORD-001."""
    return call_the_tool(order_id)


if __name__ == "__main__":
    print("MCP server listening on http://127.0.0.1:8000/mcp")
    print("It binds to localhost only. A cloud agent cannot reach your laptop.")
    server.run(transport="streamable-http")
