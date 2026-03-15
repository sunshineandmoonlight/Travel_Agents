# Kill processes using port 8004
Write-Host "Finding processes using port 8004..."

$port = 8004
$pids = netstat -ano | Select-String ":$port" | ForEach-Object {
    $_.ToString().Trim().Split()[-1]
} | Select-Object -Unique

Write-Host "Found PIDs: $($pids -join ', ')"

foreach ($pid in $pids) {
    try {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Killing process $pid - $($process.ProcessName)"
            Stop-Process -Id $pid -Force
        } else {
            Write-Host "Process $pid not found, trying taskkill..."
            cmd /c "taskkill /F /PID $pid" 2>$null
        }
    } catch {
        Write-Host "Error killing process $pid: $_"
    }
}

# Verify
Start-Sleep -Seconds 1
$remaining = netstat -ano | Select-String ":$port"
if ($remaining) {
    Write-Host "WARNING: Port $port still in use!"
} else {
    Write-Host "SUCCESS: Port $port is now free!"
}
