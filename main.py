import os
import httpx
import anyio
from dotenv import load_dotenv
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

load_dotenv()

API_CLIENT_ID = os.getenv("BOLAGSVERKET_API_CLIENT_ID")
API_CLIENT_SECRET = os.getenv("BOLAGSVERKET_API_CLIENT_SECRET")
BASE_URL = "https://gw-accept2.api.bolagsverket.se/vardefulla-datamangder/v1"
TOKEN_URL = "https://portal-accept2.api.bolagsverket.se/oauth2/token"

if not API_CLIENT_ID or not API_CLIENT_SECRET:
    raise ValueError("BOLAGSVERKET_API_CLIENT_ID and BOLAGSVERKET_API_CLIENT_SECRET must be set in .env file")

async def get_access_token():
    """Fetches an access token from the Bolagsverket API."""
    data = {
        "grant_type": "client_credentials",
        "client_id": API_CLIENT_ID,
        "client_secret": API_CLIENT_SECRET,
        "scope": "vardefulla-datamangder:read vardefulla-datamangder:ping"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        return response.json()["access_token"]

async def is_alive():
    """Checks if the Bolagsverket API is available."""
    access_token = await get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/isalive", headers=headers)
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

async def get_organisation(identitetsbeteckning: str):
    """Retrieves data about a company."""
    access_token = await get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {"identitetsbeteckning": identitetsbeteckning}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/organisationer", json=data, headers=headers)
        response.raise_for_status()
        return [types.JsonContent(type="json", json=response.json())]

async def get_document_list(identitetsbeteckning: str):
    """Retrieves a list of available annual reports for a company."""
    access_token = await get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {"identitetsbeteckning": identitetsbeteckning}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/dokumentlista", json=data, headers=headers)
        response.raise_for_status()
        return [types.JsonContent(type="json", json=response.json())]

async def get_document(document_id: str):
    """Retrieves an annual report."""
    access_token = await get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/dokument/{document_id}", headers=headers)
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

def main():
    app = Server("bolagsverket-mcp-server")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "is_alive":
            return await is_alive()
        elif name == "get_organisation":
            return await get_organisation(arguments["identitetsbeteckning"])
        elif name == "get_document_list":
            return await get_document_list(arguments["identitetsbeteckning"])
        elif name == "get_document":
            return await get_document(arguments["document_id"])
        else:
            raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools():
        return [
            types.Tool(
                name="is_alive",
                title="Is Alive",
                description="Checks if the Bolagsverket API is available.",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="get_organisation",
                title="Get Organisation",
                description="Retrieves data about a company.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "identitetsbeteckning": {"type": "string"}
                    },
                    "required": ["identitetsbeteckning"]
                }
            ),
            types.Tool(
                name="get_document_list",
                title="Get Document List",
                description="Retrieves a list of available annual reports for a company.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "identitetsbeteckning": {"type": "string"}
                    },
                    "required": ["identitetsbeteckning"]
                }
            ),
            types.Tool(
                name="get_document",
                title="Get Document",
                description="Retrieves an annual report.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"}
                    },
                    "required": ["document_id"]
                }
            )
        ]

    async def arun():
        async with stdio_server() as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    anyio.run(arun)
    return 0

if __name__ == "__main__":
    main()
