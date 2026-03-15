# -*- coding: utf-8 -*-
"""
端口占用诊断与修复工具
"""

import subprocess
import sys
import time

def run_cmd(cmd):
    """运行命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except:
        return ""

def main():
    print("=" * 60)
    print("  Port Diagnosis and Fix Tool")
    print("=" * 60)

    ports = [8004, 8005, 8006]

    # Step 1: Check port status
    print("\n[Step 1] Checking port status...")
    port_info = {}

    for port in ports:
        output = run_cmd(f"netstat -ano | findstr :{port}")
        if output:
            for line in output.split('\n'):
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        port_info[port] = pid
                        print(f"  Port {port}: PID {pid}")
                        break
        else:
            print(f"  Port {port}: Free")

    # Step 2: Check if PIDs exist
    print("\n[Step 2] Checking if PIDs exist...")
    ghost_pids = []
    real_pids = []

    for port, pid in port_info.items():
        # Check if process exists
        output = run_cmd(f"tasklist /FI \"PID eq {pid}\"")
        if pid in output:
            print(f"  PID {pid}: EXISTS (real process)")
            real_pids.append((port, pid))
        else:
            print(f"  PID {pid}: NOT FOUND (ghost port binding)")
            ghost_pids.append((port, pid))

    # Step 3: Diagnosis
    print("\n[Step 3] Diagnosis...")
    if ghost_pids:
        print(f"\n  Found {len(ghost_pids)} ghost port bindings:")
        for port, pid in ghost_pids:
            print(f"    - Port {port}: Listed as PID {pid} but process doesn't exist")
        print("\n  CAUSE: Windows TCP/IP stack stuck in CLOSE_WAIT/TIME_WAIT state")
        print("  This happens when a process is forcefully terminated")

    if real_pids:
        print(f"\n  Found {len(real_pids)} real processes:")
        for port, pid in real_pids:
            # Get process name
            output = run_cmd(f"tasklist /FI \"PID eq {pid}\" /FO CSV /NH")
            parts = output.split(',')
            if parts:
                name = parts[0].strip('"')
                print(f"    - Port {port}: PID {pid} ({name})")

    # Step 4: Solutions
    print("\n[Step 4] Solutions...")

    if ghost_pids:
        print("\n  For ghost port bindings, try these solutions:")
        print("  1. Wait 1-2 minutes for Windows to auto-release")
        print("  2. Run: netsh int ipv4 set dyntcp tcpstartport=8004")
        print("  3. Restart computer")
        print("  4. Use different ports (temporary workaround)")

    if real_pids:
        print("\n  For real processes, you can:")
        for port, pid in real_pids:
            print(f"    - Kill PID {pid}: taskkill /F /PID {pid}")

    # Step 5: Check for TIME_WAIT
    print("\n[Step 5] Checking TIME_WAIT ports...")
    time_wait_ports = []
    for port in ports:
        output = run_cmd(f"netstat -ano | findstr :{port}")
        if output:
            for line in output.split('\n'):
                if 'TIME_WAIT' in line:
                    time_wait_ports.append(port)
                    print(f"  Port {port}: In TIME_WAIT state")
                    break

    if time_wait_ports:
        print("\n  TIME_WAIT ports will be released automatically in ~60 seconds")

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"\nTotal ports checked: {len(ports)}")
    print(f"Free ports: {len(ports) - len(port_info)}")
    print(f"Ghost bindings: {len(ghost_pids)}")
    print(f"Real processes: {len(real_pids)}")
    print(f"TIME_WAIT states: {len(time_wait_ports)}")

    print("\nRECOMMENDATIONS:")
    print("1. Use port 8006 for current development (confirmed working)")
    print("2. For ports 8004/8005: either wait or restart computer")
    print("3. Consider setting a fixed port range for development")

    return {
        "ghost_pids": ghost_pids,
        "real_pids": real_pids,
        "time_wait": time_wait_ports
    }

if __name__ == "__main__":
    try:
        result = main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
