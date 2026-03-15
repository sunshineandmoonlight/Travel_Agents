# -*- coding: utf-8 -*-
"""
诊断端口占用问题 - 找出根本原因
"""

import subprocess
import psutil
import sys
import os

def run_command(cmd):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1

def find_processes_on_port(port):
    """查找占用指定端口的进程"""
    print(f"\n=== 查找占用端口 {port} 的进程 ===")

    # 方法1: netstat
    print("\n[方法1] 使用 netstat:")
    stdout, stderr, code = run_command(f"netstat -ano | findstr :{port}")
    if stdout:
        for line in stdout.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 5 and 'LISTENING' in line:
                pid = parts[-1]
                print(f"  发现进程: PID {pid}")
                return [pid]
    else:
        print("  未找到监听的进程")

    return []

def get_process_info(pid):
    """获取进程详细信息"""
    print(f"\n=== 获取进程 {pid} 的详细信息 ===")

    try:
        proc = psutil.Process(int(pid))

        print(f"\n进程名称: {proc.name()}")
        print(f"PID: {proc.pid}")
        print(f"状态: {proc.status()}")
        print(f"可执行路径: {proc.exe()}")

        # 获取命令行参数
        try:
            cmdline = proc.cmdline()
            print(f"命令行: {' '.join(cmdline)}")
        except:
            print("命令行: 无法获取")

        # 获取父进程
        try:
            parent = proc.parent()
            if parent:
                print(f"父进程: {parent.name()} (PID: {parent.pid})")
        except:
            print("父进程: 无法获取")

        # 获取创建时间
        create_time = proc.create_time()
        from datetime import datetime
        create_dt = datetime.fromtimestamp(create_time)
        print(f"启动时间: {create_dt.strftime('%Y-%m-%d %H:%M:%S')}")

        # 获取连接信息
        try:
            connections = proc.connections(kind='inet')
            print(f"\n网络连接 ({len(connections)} 个):")
            for conn in connections[:10]:
                if conn.laddr:
                    print(f"  本地: {conn.laddr.ip}:{conn.laddr.port} -> 状态: {conn.status}")
        except:
            print("网络连接: 无法获取")

        return proc

    except psutil.NoSuchProcess:
        print(f"进程 {pid} 不存在")
        return None
    except Exception as e:
        print(f"获取进程信息失败: {e}")
        return None

def find_all_python_processes():
    """查找所有Python进程"""
    print("\n=== 查找所有 Python 进程 ===")

    python_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and ('uvicorn' in ' '.join(cmdline) or 'main:app' in ' '.join(cmdline)):
                    python_procs.append(proc)
                    print(f"\nPID {proc.info['pid']}: {' '.join(cmdline[:3])}")
        except:
            pass

    return python_procs

def kill_process_tree(pid):
    """强制终止进程树（包括子进程）"""
    print(f"\n=== 尝试终止进程树 {pid} ===")

    try:
        proc = psutil.Process(int(pid))

        # 获取所有子进程
        children = proc.children(recursive=True)

        print(f"找到 {len(children)} 个子进程")

        # 先终止子进程
        for child in children:
            try:
                print(f"  终止子进程 {child.pid}")
                child.terminate()
            except:
                pass

        # 等待一下
        import time
        time.sleep(1)

        # 终止主进程
        print(f"  终止主进程 {pid}")
        proc.terminate()

        # 如果 terminate 不行，用 kill
        time.sleep(2)
        if proc.is_running():
            print(f"  terminate 无效，使用 kill")
            proc.kill()

        time.sleep(1)

        if not proc.is_running():
            print(f"  ✅ 进程 {pid} 已终止")
            return True
        else:
            print(f"  ❌ 进程 {pid} 仍在运行")
            return False

    except psutil.NoSuchProcess:
        print(f"  ✅ 进程 {pid} 已不存在")
        return True
    except Exception as e:
        print(f"  ❌ 终止失败: {e}")
        return False

def diagnose_port_issue():
    """诊断端口占用问题的根本原因"""

    print("=" * 60)
    print("  端口占用问题诊断工具")
    print("=" * 60)

    # 检查端口 8004, 8005, 8006
    ports = [8004, 8005, 8006]
    occupied_ports = {}

    for port in ports:
        pids = find_processes_on_port(port)
        if pids:
            occupied_ports[port] = pids[0]

    print(f"\n=== 端口占用汇总 ===")
    for port, pid in occupied_ports.items():
        print(f"  端口 {port}: 被 PID {pid} 占用")

    if not occupied_ports:
        print("  所有端口都空闲")
        return

    # 获取占用进程的详细信息
    for port, pid in occupied_ports.items():
        proc = get_process_info(pid)

        # 检查是否是僵尸进程
        if proc:
            try:
                if proc.status() == psutil.STATUS_ZOMBIE:
                    print(f"\n  ⚠️ 警告: 进程 {pid} 是僵尸进程!")
                elif not proc.is_running():
                    print(f"\n  ⚠️ 警告: 进程 {pid} 已停止但端口仍被占用!")
            except:
                pass

    # 查找所有相关的 Python/uvicorn 进程
    print("\n" + "=" * 60)
    python_procs = find_all_python_processes()

    # 分析原因
    print("\n=== 问题分析 ===")

    if occupied_ports:
        print("\n可能的根本原因:")
        print("1. 进程没有正确处理关闭信号")
        print("2. 有子进程仍在运行")
        print("3. 端口被Windows系统保留（TIME_WAIT状态）")
        print("4. 防火墙或安全软件锁定")

    # 尝试修复
    if occupied_ports:
        print("\n=== 尝试自动修复 ===")

        for port, pid in list(occupied_ports.items()):
            print(f"\n处理端口 {port} (PID {pid}):")
            kill_process_tree(pid)

        # 重新检查
        print("\n=== 重新检查端口 ===")
        for port in ports:
            pids = find_processes_on_port(port)
            if pids:
                print(f"  端口 {port}: 仍被占用")
            else:
                print(f"  端口 {port}: ✅ 已释放")

if __name__ == "__main__":
    try:
        diagnose_port_issue()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n诊断出错: {e}")
        import traceback
        traceback.print_exc()
