from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
import asyncio

def handle_osc(address, *args):
    print(f"Received {address}: {args[0]}\t {args[1]}\t{args[2]}")

async def main():
    print('tracking...')
    dispatcher = Dispatcher()
    dispatcher.map("/tracking/trackers/8/rotation", handle_osc)
    
    server = AsyncIOOSCUDPServer(("127.0.0.1", 9000), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()
    
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
