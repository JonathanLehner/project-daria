from pythonosc import udp_client
import asyncio
import random
import math

def generate_rotation_data():
    """Generate dummy rotation data (Euler angles)"""
    x = random.uniform(-10, 10)
    y = random.uniform(-10, 10)
    z = random.uniform(-10, 10)
    return x, y, z

class DummyDataServer:
    def __init__(self, ip="127.0.0.1", port=9000):
        self.client = udp_client.SimpleUDPClient(ip, port)
        self.running = False
        self.task = None
        self.counter = 0
    
    async def run(self):
        """Main loop to send rotation data"""
        self.running = True
        print("Dummy data server started, sending rotation data...")
        
        while self.running:
            # Generate random rotation values
            x, y, z = generate_rotation_data()
            
            # Send OSC message with 3 arguments
            self.client.send_message("/tracking/trackers/8/rotation", [x, y, z])
            
            self.counter += 1
            # print(f"Sent rotation data #{self.counter}: x={x:.3f}, y={y:.3f}, z={z:.3f}")
            
            # Wait before sending next message
            await asyncio.sleep(0.5)  # 2 messages per second
            
        print("Dummy data server stopped.")
    
    def start(self):
        """Start the server in the background"""
        if self.task is None or self.task.done():
            loop = asyncio.get_event_loop()
            self.task = loop.create_task(self.run())
        return self.task
    
    def stop(self):
        """Stop the server"""
        self.running = False

async def main():
    """Example of how to use the DummyDataServer"""
    server = DummyDataServer()
    try:
        await server.run()
    except KeyboardInterrupt:
        server.stop()

if __name__ == "__main__":
    asyncio.run(main())