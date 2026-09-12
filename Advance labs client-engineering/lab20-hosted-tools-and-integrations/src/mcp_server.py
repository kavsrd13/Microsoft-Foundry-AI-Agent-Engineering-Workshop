from mcp.server.fastmcp import FastMCP
from call_tool import get_order_status

mcp = FastMCP('Council orders', host='127.0.0.1', port=8000)
mcp.tool()(get_order_status)
if __name__ == '__main__':
    mcp.run(transport='streamable-http')
