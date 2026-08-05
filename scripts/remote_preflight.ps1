$ErrorActionPreference = "Stop"

$LinuxHost = "mxadmin@192.168.58.133"
$ProjectPath = "/home/mxadmin/ymatrix-mysql-benchmark"

$RemoteCommand = @(
    "set -e"
    "test -d '$ProjectPath/.git' || { echo 'ERROR: Linux project is not a Git repository: $ProjectPath' >&2; exit 10; }"
    "test -f '$ProjectPath/config.local.json' || { echo 'ERROR: config.local.json does not exist' >&2; exit 11; }"
    "cd '$ProjectPath'"
    "echo '=== Pull source ==='"
    "git pull --ff-only"
    "echo '=== Python version ==='"
    "python3 --version"
    "echo '=== Syntax check ==='"
    "python3 -m compileall -q run.py src tests"
    "echo '=== Unit tests ==='"
    "python3 -m unittest discover -s tests -v"
    "echo '=== Database preflight ==='"
    "python3 run.py preflight --config config.local.json"
) -join "; "

& ssh $LinuxHost $RemoteCommand

if ($LASTEXITCODE -ne 0) {
    throw "Linux remote preflight failed with exit code $LASTEXITCODE"
}

Write-Host "Linux remote preflight completed successfully."