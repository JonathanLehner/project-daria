from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
import asyncio
import numpy as np

# Import the DummyDataServer class
from dummy_data_server import DummyDataServer
import os
from datetime import datetime

SERVER_IP = "127.0.0.1" # The IP address to listen for OSC messages
SERVER_PORT = 9000  # The port to listen for OSC messages
TRACKER_ID = 8  # The ID of the tracker to listen to (change to "*" to listen to all trackers)
USE_DUMMY_DATA = False  # Set to False to use real data
VERBOSE = True  # Set to True to enable verbose output

class RotationTracker:
    def __init__(self, calibration_samples=10, verbose=True):
        self.calibration_samples = calibration_samples
        self.samples_collected = 0
        self.calibration_data = []
        self.calibration_complete = False
        self.reference_rotation = None
        self.verbose = verbose
        
        # Create posedata folder if it doesn't exist
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posedata")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create a timestamped file for data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.data_file = os.path.join(self.data_dir, f"rotation_data_{timestamp}.csv")
        
        # Create and write header to file
        with open(self.data_file, "w") as f:
            f.write("timestamp,x,y,z,dx,dy,dz\n")
    
    def handle_rotation(self, address, *args):
        """Handle incoming OSC messages with calibration logic."""
        x, y, z = args
        current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        
        if not self.calibration_complete:
            # Still in calibration phase
            self.calibration_data.append((x, y, z))
            self.samples_collected += 1
            if self.verbose:
                print(f"Calibration sample {self.samples_collected}/{self.calibration_samples}: x={x:.3f}, y={y:.3f}, z={z:.3f}")
            
            if self.samples_collected >= self.calibration_samples:
                # Complete calibration
                self._complete_calibration()
                print("Calibration complete! Now tracking rotation offsets.")
        else:
            # Compute offset from calibration
            dx = x - self.reference_rotation[0]
            dy = y - self.reference_rotation[1]
            dz = z - self.reference_rotation[2]
            
            # Save data to file
            with open(self.data_file, "a") as f:
                f.write(f"{current_time},{x:.6f},{y:.6f},{z:.6f},{dx:.6f},{dy:.6f},{dz:.6f}\n")
            
            if self.verbose:
                print(f"Rotation offset: \t dx={dx:.3f}\t dy={dy:.3f}\t dz={dz:.3f}")
            
            if self._alert_rotation(dx, dy, dz):
                print(f"Alert! Significant rotation detected: dx={dx:.3f}, dy={dy:.3f}, dz={dz:.3f}")

    def _alert_rotation(self, dx, dy, dz):
        """Check if the rotation exceeds a certain threshold."""
        # TODO Define a correct function to check along wanted axis
        threshold = 60.0
        # if abs(dx) > threshold or abs(dy) > threshold or abs(dz) > threshold:
        if abs(dz) > threshold:
            return True

    def _complete_calibration(self):
        """Calculate reference rotation from collected samples."""
        data = np.array(self.calibration_data)
        # TODO: use better calibration method/ average angles better.
        self.reference_rotation = np.mean(data, axis=0)
        print(f"Reference rotation set to: x={self.reference_rotation[0]:.3f}, y={self.reference_rotation[1]:.3f}, z={self.reference_rotation[2]:.3f}")
        self.calibration_complete = True

async def main():
    print('Setting up...')
    
    # Create the rotation tracker
    rotation_tracker = RotationTracker(verbose=VERBOSE)
    
    # Set up the OSC server to listen for messages
    dispatcher = Dispatcher()
    tracker_address = f"/tracking/trackers/{TRACKER_ID}/rotation"
    dispatcher.map(tracker_address, rotation_tracker.handle_rotation)
    
    server = AsyncIOOSCUDPServer((SERVER_IP, SERVER_PORT), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()
    
    # If using dummy data, start the dummy server to generate messages
    dummy_server = None
    if USE_DUMMY_DATA:
        print('Using dummy data server...')
        dummy_server = DummyDataServer(ip=SERVER_IP, port=SERVER_PORT)
        dummy_task = asyncio.create_task(dummy_server.run())
    else:
        print('Listening for real data...')
    
    try:
        # Main loop
        while True:
            await asyncio.sleep(1)
    finally:
        # Clean up
        if dummy_server:
            dummy_server.stop()
        transport.close()

# Run the main coroutine and handle keyboard interrupt
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Shutting down...")
