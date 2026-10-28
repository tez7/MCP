from mcp.server.mcpserver import MCPServer # neede this module whenever we need to build mcp server
import math

mcp = MCPServer("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    return a * b

@mcp.tool()
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Division by 0 not possible")
    return a / b

@mcp.tool()
def Square_root(x: float) -> float:
    if x < 0:
        raise ValueError(" can't be neagtive")
    return math.sqrt(x) 

@mcp.tool()
def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial not define for negative number")
    return math.factorial(n)

if __name__ == "__main__":
    # mcp.run(transport="stdio") # if client and server both at local
    mcp.run(transport = "streamable-http") # if server at remote or browser or internet