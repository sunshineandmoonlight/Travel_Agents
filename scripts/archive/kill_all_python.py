"""Force kill all Python processes and clean port 8004"""
import subprocess
import time

print("=== Forcing cleanup of port 8004 ===\n")

# 1. Kill all python.exe and pythonw.exe processes
print("[1/3] Killing all Python processes...")
result = subprocess.run(
    ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
    capture_output=True,
    text=True
)

python_pids = []
for line in result.stdout.split('\n'):
    if 'python.exe' in line:
        parts = line.split()
        for part in parts:
            if part.isdigit():
                python_pids.append(part)
                break

if python_pids:
    for pid in set(python_pids):
        print(f"  Killing Python process {pid}...")
        subprocess.run(['taskkill', '/F', '/PID', pid],
                      capture_output=True)
else:
    print("  No Python processes found")

# 2. Kill pythonw.exe too
print("\n[2/3] Killing all Pythonw processes...")
result = subprocess.run(
    ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe'],
    capture_output=True,
    text=True
)

pythonw_pids = []
for line in result.stdout.split('\n'):
    if 'pythonw.exe' in line:
        parts = line.split()
        for part in parts:
            if part.isdigit():
                pythonw_pids.append(part)
                break

if pythonw_pids:
    for pid in set(pythonw_pids):
        print(f"  Killing Pythonw process {pid}...")
        subprocess.run(['taskkill', '/F', '/PID', pid],
                      capture_output=True)
else:
    print("  No Pythonw processes found")

# 3. Wait and verify
print("\n[3/3] Waiting for ports to be released...")
time.sleep(3)

# Check if port is free
result = subprocess.run(
    ['netstat', '-ano'],
    capture_output=True,
    text=True
)

port_8004_in_use = False
for line in result.stdout.split('\n'):
    if ':8004' in line and 'LISTENING' in line:
        port_8004_in_use = True
        print(f"  Port still in use: {line.strip()}")
        # Extract PID and try to kill it
        parts = line.split()
        if parts:
            pid = parts[-1]
            if pid.isdigit():
                print(f"  Force killing PID {pid}...")
                subprocess.run(['taskkill', '/F', '/PID', pid],
                              capture_output=True)

if not port_8004_in_use:
    print("\n✓ SUCCESS: Port 8004 is now free!")
else:
    print("\n✗ FAILED: Port 8004 still in use")
    print("Please manually run: taskkill /F /PID <PID>")
    print("Or restart your computer.")
