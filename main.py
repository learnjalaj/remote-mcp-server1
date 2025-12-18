import os
import random
import json
from fastmcp import FastMCP

mcp = FastMCP("Simple Calculator Server")

#Tool: add two numbers
@mcp.tool()
def add(a:int,b:int)->int:
    """
    Add two numbers together.
    args:
    a: First number
    b: second number
    returns:
    sum of a and b
    """
    return a+b
    
#Tool: generate a random number
@mcp.tool()
def random_num(min_val:int=1,max_val:int=100)->int:
    """
    Generate a random number within a range.
    args:
    min_val: Minimum value (default = 1)
    max_val: Maximum value (default = 100)
    returns:
    A random number between min_val and max_val
    """
    return random.randint(min_val,max_val)

@mcp.resource("info://server")
def server_invo()->str:
    """Get information about the server"""
    info = {
        "name":"Simple Calculator Service",
        "version":"1.0.0",
        "description":"A basic MCP server with math tools",
        "tools":["add","random_number"],
        "author":"Jalaj"
    }
    return json.dumps(info,indent=2)

if __name__ == "__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8000)