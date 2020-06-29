import time
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative

connection_string = "udp:127.0.0.1:14551"
print(f"Connecting to vehicle on: {connection_string}")

vehicle = connect(connection_string, wait_ready=True)

while not vehicle.is_armable:
    print(" Waiting for vehicle to initialise...")
    time.sleep(1)

print("Arming motors")
vehicle.mode = VehicleMode("MANUAL")
vehicle.armed = True

while not vehicle.armed:
    print (" Waiting for arming...")
    time.sleep(1)