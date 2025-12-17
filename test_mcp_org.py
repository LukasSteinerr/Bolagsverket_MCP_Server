import asyncio
import os
import json
import httpx
from main import is_alive, get_organisation

async def test_server():
    print("Testing Bolagsverket MCP Server...")
    
    try:
        # 1. Test is_alive
        print("\nTesting 'is_alive'...")
        alive_result = await is_alive()
        print(f"Result: {alive_result[0].text}")
        
        # 2. Test get_organisation with a dummy ID to get the list of allowed IDs
        print("\nTesting 'get_organisation' with a dummy ID to get the list of allowed test numbers...")
        try:
            await get_organisation("556000-0000")
        except httpx.HTTPStatusError as e:
            print(f"Received expected {e.response.status_code} error response.")
            if e.response.status_code == 400:
                print("This is the expected behavior for an invalid test organization number.")
                try:
                    error_json = e.response.json()
                    print("The API returned the following information, which should contain the allowed test numbers:")
                    print(json.dumps(error_json, indent=2))
                except json.JSONDecodeError:
                    print("The error response was not in JSON format. Response text:")
                    print(e.response.text)
            else:
                print("Received an unexpected HTTP error.")
                print(f"Status code: {e.response.status_code}")
                print(f"Response: {e.response.text}")

    except Exception as e:
        print(f"\nAn unexpected error occurred during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_server())
