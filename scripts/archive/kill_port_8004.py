"""Kill processes using port 8004"""
import subprocess
import sys

def kill_processes_on_port(port):
    """Kill all processes using the given port"""
    # Find PIDs using the port
    result = subprocess.run(
        ['netstat', '-ano'],
        capture_output=True,
        text=True
    )

    pids = set()
    for line in result.stdout.split('\n'):
        if f':{port}' in line and 'LISTENING' in line:
            parts = line.split()
            if parts:
                pid = parts[-1]
                if pid.isdigit():
                    pids.add(int(pid))

    print(f"Found PIDs using port {port}: {pids}")

    # Kill each process
    for pid in pids:
        try:
            print(f"Killing process {pid}...")
            subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                          capture_output=True,
                          text=True)
            print(f"  Killed process {pid}")
        except Exception as e:
            print(f"  Error killing process {pid}: {e}")

    # Verify
    print("\nVerifying...")
    result = subprocess.run(
        ['netstat', '-ano', '|', 'findstr', f':{port}'],
        shell=True,
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        print(f"WARNING: Port {port} still in use!")
        print(result.stdout)
        return False
    else:
        print(f"SUCCESS: Port {port} is now free!")
        return True

if __name__ == "__main__":
    success = kill_processes_on_port(8004)
    sys.exit(0 if success else 1)
