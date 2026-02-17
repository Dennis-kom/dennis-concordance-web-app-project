#!/usr/bin/env python
import subprocess
import socket
import time

def is_port_open(host, port):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

# Check if Docker containers are running
print("=" * 70)
print("CHECKING APPLICATION STATUS")
print("=" * 70)

# Wait for services
print("\n[1] Checking if port 5000 (Flask app) is accessible...")
if is_port_open('127.0.0.1', 5000):
    print("✓ Port 5000 is open - Flask app is running!")
else:
    print("✗ Port 5000 is closed - Flask app may not be running")

print("\n[2] Checking if port 1521 (Oracle DB) is accessible...")
if is_port_open('127.0.0.1', 1521):
    print("✓ Port 1521 is open - Oracle DB is running!")
else:
    print("✗ Port 1521 is closed - Oracle DB may not be running")

print("\n[3] Checking Docker container status...")
result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'],
                       capture_output=True, text=True)
if result.stdout:
    print(result.stdout)
else:
    print("No containers running")

print("\n[4] Trying to fetch the application homepage...")
try:
    import urllib.request
    response = urllib.request.urlopen('http://127.0.0.1:5000/', timeout=5)
    print(f"✓ Successfully connected! Status: {response.status}")
except Exception as e:
    print(f"✗ Connection failed: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("ACCESS YOUR APPLICATION AT: http://localhost:5000")
print("=" * 70)

