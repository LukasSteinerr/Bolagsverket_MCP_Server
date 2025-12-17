import asyncio
import os
import json
from main import is_alive, get_organisation, get_document_list

async def test_server():
    print("Testing Bolagsverket MCP Server...")
    
    try:
        # 1. Test is_alive
        print("\nTesting 'is_alive'...")
        alive_result = await is_alive()
        print(f"Result: {alive_result[0].text}")
        
        # 2. Test get_organisation (using a sample registration number from documentation context if possible, otherwise a dummy)
        # Note: The guide says "The test environment imposes restrictions on the company registration numbers..."
        # We'll try a dummy one first to see if it gives us the list of allowed ones as per documentation.
        print("\nTesting 'get_organisation' with dummy ID...")
        try:
            org_result = await get_organisation("556000-0000")
            print(f"Result: {org_result[0].json}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP Status Error: {e.status_code}")
            try:
                print(f"Response Body: {e.response.text}")
            except:
                pass
        except Exception as e:
            print(f"Expected error or result: {e}")

        # 3. Test get_document_list
        print("\nTesting 'get_document_list' with dummy ID...")
        try:
            doc_list = await get_document_list("556000-0000")
            print(f"Result: {doc_list[0].json}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP Status Error: {e.status_code}")
            try:
                print(f"Response Body: {e.response.text}")
            except:
                pass
        except Exception as e:
            print(f"Expected error or result: {e}")

    except Exception as e:
        print(f"\nAn error occurred during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_server())
