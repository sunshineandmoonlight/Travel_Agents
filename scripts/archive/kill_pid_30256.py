"""Force kill a specific PID"""
import subprocess
import time

pid = 30256

print(f"Attempting to kill PID {pid}...")

# Method 1: taskkill
try:
    result = subprocess.run(
        ['taskkill', '/F', '/PID', str(pid)],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"taskkill result: {result.returncode}")
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
except Exception as e:
    print(f"taskkill error: {e}")

# Wait
time.sleep(2)

# Method 2: wmic
try:
    result = subprocess.run(
        ['wmic', 'process', 'where', f'ProcessId={pid}', 'delete'],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"wmic result: {result.returncode}")
    print(f"stdout: {result.stdout}")
except Exception as e:
    print(f"wmic error: {e}")

# Wait and check
time.sleep(2)
print(f"\nChecking port 8004...")
result = subprocess.run(
    ['netstat', '-ano', '|', 'findstr', ':8004'],
    shell=True,
    capture_output=True,
    text=True
)

if result.stdout.strip():
    print("Port 8004 STILL IN USE:")
    print(result.stdout)
else:
    print("Port 8004 is NOW FREE!")
