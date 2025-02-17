import asyncio
from bleak import BleakScanner
import socket
import time

esp32_address1 = "5C:01:3B:4D:52:0E"
esp32_address2 = "08:B6:1F:B8:59:32" 
esp32_address3 = "3C:8A:1F:A3:42:96"

rssi = {}

async def scan():
    try:
        print("Starting scan...")
        scanner = BleakScanner()
        await scanner.start()
        await asyncio.sleep(10)  # Scan for 10 seconds
        await scanner.stop()

        devices = scanner.discovered_devices
        if devices:
            for device in devices:
                # Attempt to access RSSI directly
                rssi_value = device.rssi
                if device.address in {esp32_address1, esp32_address2, esp32_address3}:
                    if rssi_value is not None:
                        rssi[device.address] = rssi_value
        else:
            print("No devices found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def send_rssi_to_server(rssi_data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
            c.connect(('192.168.210.1',4040))  # Replace with your server IP and port
            print("Connected to server")

            # Format RSSI data as a list of values
            rssi_values = [str(rssi_data.get(addr, '')) for addr in [esp32_address1, esp32_address2, esp32_address3]]
            rssi_message = '\n'.join(rssi_values) + '\n'
            
            print(f"Sending to server:\n{rssi_message.strip()}")
            c.sendall(rssi_message.encode('utf-8'))
    except socket.error as e:
        print(f"Socket error: {e}")

async def periodic_scan_and_send(interval):
    while True:
        await scan()  # Perform the scan and update RSSI values
        if rssi:
            send_rssi_to_server(rssi)  # Send RSSI values to server
        await asyncio.sleep(interval)  # Wait for the specified interval

async def main():
    await periodic_scan_and_send(2)  # Update and send every 5 seconds

if __name__ == "__main__":
    asyncio.run(main())
