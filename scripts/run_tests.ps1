<#
Run pytest with a configurable timeout to avoid hanging CI runs.
Usage: .\run_tests.ps1 -TimeoutSeconds 300
#>

param(
    [int]$TimeoutSeconds = 300
)

Write-Host "Starting pytest with timeout ${TimeoutSeconds}s..."

$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = "python"
$startInfo.Arguments = "-m pytest -q --maxfail=1"
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $startInfo
$process.Start() | Out-Null

$outputBuilder = New-Object System.Text.StringBuilder

$stdoutReader = $process.StandardOutput
$stderrReader = $process.StandardError

$startTime = Get-Date

while (-not $process.HasExited) {
    $line = $stdoutReader.ReadLine()
    if ($line) { Write-Host $line }
    if ((Get-Date) - $startTime -gt (New-TimeSpan -Seconds $TimeoutSeconds)) {
        Write-Warning "Test run exceeded timeout of ${TimeoutSeconds} seconds. Terminating pytest..."
        $process.Kill()
        break
    }
    Start-Sleep -Milliseconds 100
}

# Print remaining buffers
while (-not $stdoutReader.EndOfStream) {
    Write-Host $stdoutReader.ReadLine()
}

while (-not $stderrReader.EndOfStream) {
    Write-Host $stderrReader.ReadLine()
}

if ($process.ExitCode -ne 0) {
    Write-Error "Pytest finished with exit code $($process.ExitCode)"
    exit $process.ExitCode
}

Write-Host "Pytest completed successfully."
