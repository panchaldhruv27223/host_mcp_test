# from fastmcp import FastMCP
# import asyncio
# from db import init_db, save_message, fetch_messages
# from pydantic import BaseModel

# class SaveMessageInput(BaseModel):
#     user_id: str
#     message: str

# class GetMessagesInput(BaseModel):
#     user_id: str


# app = FastMCP("sqlite-mcp-server")

# # print(dir(app))

# init_db()

# @app.tool()
# def save_user_message(data: SaveMessageInput):
#     """Save a message into the SQLite database."""
#     save_message(data.user_id, data.message)
#     return {"status": "saved", "user_id": data.user_id}

# @app.tool()
# def get_user_messages(data: GetMessagesInput):
#     """Retrieve all messages for the given user."""
#     rows = fetch_messages(data.user_id)
#     messages = [
#         {
#             "id": r[0],
#             "message": r[1],
#             "created_at": r[2],
#         }
#         for r in rows
#     ]
#     return {"user_id": data.user_id, "messages": messages}


# # @app.custom_route("/", methods=["GET"])
# # def root():
# #     return {"status": "ok", "message": "MCP server is running"}



# if __name__ == "__main__":
#     app.run()
#     # asyncio.run(app(transport="http", host="0.0.0.0"))

# import os
# from fastmcp import FastMCP
# from pydantic import BaseModel
# from starlette.responses import JSONResponse
# from db import init_db, save_message, fetch_messages

# class SaveMessageInput(BaseModel):
#     user_id: str
#     message: str

# class GetMessagesInput(BaseModel):
#     user_id: str

# app = FastMCP("sqlite-mcp-server")

# init_db()

# @app.tool()
# def save_user_message(data: SaveMessageInput):
#     save_message(data.user_id, data.message)
#     return {"status": "saved", "user_id": data.user_id}

# @app.tool()
# def get_user_messages(data: GetMessagesInput):
#     rows = fetch_messages(data.user_id)
#     return {
#         "user_id": data.user_id,
#         "messages": [
#             {"id": r[0], "message": r[1], "created_at": r[2]} for r in rows
#         ]
#     }

# @app.custom_route("/health", methods=["GET"])
# async def health(request):
#     return JSONResponse({"status": "healthy"})

# if __name__ == "__main__":
#     app.run(
#         transport="http",
#         host="0.0.0.0",
#         port=int(os.getenv("PORT", 8000))
#     )




# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel
# from typing import Optional, Union, Dict, Any
# from mcp.server import Server
# import uvicorn

# from mcp.types import Tool, TextContent
# from pydantic import Field
# from typing import List

# class MCPRequest(BaseModel):
#     jsonrpc: str = "2.0"
#     id: Optional[Union[str, int]] = None
#     method: str
#     params: Optional[Dict[str, Any]] = None

# class EchoRequest(BaseModel):
#     message: str = Field(..., description="Message to echo")
#     repeat_count: int = Field(1, ge=1, le=10)


# app = FastAPI(title="MCP Echo Server", version="0.1.0")
# server = Server("mcp-echo")

# @app.middleware("http")
# async def origin_validation_middleware(request: Request, call_next):
#     """
#     Middleware to validate Origin header according to MCP specification.
#     This prevents DNS rebinding attacks by ensuring requests come from trusted origins.
#     """
#     # Skip validation for health check endpoint (optional)
#     if request.url.path == "/health":
#         response = await call_next(request)
#         return response

#     # Get the Origin header
#     origin = request.headers.get("origin")
    
#     # Allow requests with no Origin header to allow mcp-inspector to work
#     if not origin:
#         print("✅ No Origin header - allowing for MCP client")
#         response = await call_next(request)
#         return response
    
#     # Validate the origin - allow localhost and 127.0.0.1 on any port
#     if not origin.startswith("http://localhost") and not origin.startswith("http://127.0.0.1"):
#         print(f"❌ Origin '{origin}' rejected")
#         return JSONResponse(
#             status_code=403,
#             content={"detail": f"Origin '{origin}' is not allowed. Only localhost and 127.0.0.1 are permitted."}
#         )
    
#     print(f"✅ Origin '{origin}' accepted")
#     response = await call_next(request)
#     return response

# @app.get("/health")
# async def health():
#     return {"status": "healthy"}

# @app.get("/mcp")
# async def handle_mcp_get(request: Request):
#     """Handle GET requests to MCP endpoint."""
#     # Return 405 Method Not Allowed as per MCP spec for servers that don't support SSE
#     return JSONResponse(
#         status_code=405,
#         content={"detail": "Method Not Allowed - This server does not support server-initiated streaming"}
#     )

# @app.post("/mcp")
# async def handle_mcp_request(request: Request):
#     body = await request.json()
#     # print(body)
#     mcp_request = MCPRequest(**body)
#     # print(mcp_request)
#     # print(mcp_request.params)
#     if mcp_request.id is None:
#         return JSONResponse(status_code=202, content=None)
    
#     # print(mcp_request.params["name"], mcp_request.params["arguments"])

#     try:
#         if mcp_request.method == "initialize":
#             result = {
#                 "protocolVersion": "2025-06-18",
#                 "capabilities": {"tools": {"listChanged": False}},
#                 "serverInfo": {"name": "mcp-echo", "version": "0.1.0"}
#             }
#         elif mcp_request.method == "tools/list":
#             tools = await list_tools()
#             result = {
#                 "tools": [tool.model_dump() for tool in tools]
#             }
        
#         elif mcp_request.method == "tools/call":
            
#             print(mcp_request.params["name"], mcp_request.params["arguments"])
#             content = await call_tool(mcp_request.params["name"], mcp_request.params["arguments"])
#             result = {
#                 "content": [item.model_dump() for item in content],
#                 "isError": False
#             }
#         else:
#             raise ValueError("Unsupported method")

#         return JSONResponse(content={"jsonrpc": "2.0", "id": mcp_request.id, "result": result})

#     except Exception as e:
#         return JSONResponse(
#             status_code=500,
#             content={"jsonrpc": "2.0", "id": mcp_request.id, "error": {"code": -32603, "message": str(e)}}
#         )

# @server.list_tools()
# async def list_tools() -> List[Tool]:
#     return [Tool(
#         name="echo", 
#         description="Echo a message", 
#         title="Echo Tool",
#         inputSchema=EchoRequest.model_json_schema(),
#         outputSchema={
#             "type": "object",
#             "properties": {
#                 "text": {"type": "string", "description": "The echoed message"}
#             }
#         },
#         annotations={
#             "title": "Echo Tool",
#             "readOnlyHint": False,
#             "destructiveHint": False,
#             "idempotentHint": True,
#             "openWorldHint": False
#         }
#     )]

# @server.call_tool()
# async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
#     args = EchoRequest(**arguments)
#     print("Call from call tool: ",args)
#     return [TextContent(type="text", text=args.message * args.repeat_count)]

# def main():
#     uvicorn.run(app, host="0.0.0.0", port=9000)

# if __name__ == "__main__":
#     main()




import os
from fastmcp import FastMCP
import _asyncio
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn


# class output_message(BaseModel):
#     final_output : str

# class MCPRequest(BaseModel):
#     jsonrpc: str ="2.0"
#     first_message: str
#     second_message: str
#     id: int
#     method: str    

# app = FastAPI(title="MCP Echo Server", version="0.1.0")
# mcp = FastMCP(name="remote-server", version="0.0.1")


# @mcp.tool()
# async def add_messages(mess1:str, mess2: str) -> output_message:
#     '''Take two messages as input concatenate that two messages and return new full message as output'''
    
#     return output_message(final_output = mess1 + mess2)

# # @mcp.fastapi_app.get("/health")
# # async def health():
# #     return {"status": "healthy"}

# # @mcp.fastapi_app.get("/")
# # async def health():
# #     return {"status": "Ok"}

# @app.get("/")
# async def health():
#     return {"status": "Be Ok"}

# @app.get("/health")
# async def healthy():
#     return {"status": "healthy"}


# # @app.get("/mcp")
# # async def handle_mcp_get(request: Request):
# #     """Handle GET requests to MCP endpoint."""
# #     # Return 405 Method Not Allowed as per MCP spec for servers that don't support SSE
# #     return JSONResponse(
# #         status_code=405,
# #         content={"detail": "Method Not Allowed - This server does not support server-initiated streaming"}
# #     )

# # @app.post("/mcp")
# # async def handle_mcp_request(request: Request):
# #     body = await request.json()
# #     print(body)
# #     mcp_request = MCPRequest(**body)
# #     print(mcp_request)
# #     if mcp_request.id is None:
# #         return JSONResponse(status_code=202, content=None)

# #     # return {"Mcp":"Working"}
    
# #     result = await add_messages(mcp_request.first_message, mcp_request.second_message)
    
# #     print(result)
    
# #     return result
# mcp.mount(app)


# if __name__ == "__main__":
#     # app.mount("/mcp", mcp.http_app())
#     uvicorn.run(app, host="0.0.0.0", port=9000)
#     # mcp.run(transport="sse")






## test version

from fastmcp import FastMCP

# 1. Create the server
mcp = FastMCP(name="Echo Server")

# 2. Define the Tool
@mcp.tool()
def add_messages(mess1: str, mess2: str) -> str:
    """Concatenate two messages."""
    return mess1 + mess2

# 3. Run the server using FastMCP's built-in runner
if __name__ == "__main__":
    # This automatically sets up routes and defaults to Port 8000
    mcp.run(transport="sse")