$ProjectRoot = "C:\Users\eem01063\Desktop\muaz\vt-rap"
$PythonExe = "$ProjectRoot\.venv\Scripts\python.exe"
$Today = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = "$ProjectRoot\logs\vtrap_refresh_$Today.log"

Set-Location $ProjectRoot

function Write-Log {
    param([string]$Message)

    "[$(Get-Date)] $Message" | Tee-Object -FilePath $LogFile -Append
}

function Invoke-LoggedCommand {
    param(
        [string]$StepName,
        [string]$Executable,
        [string[]]$Arguments
    )

    Write-Log $StepName

    $output = & $Executable @Arguments 2>&1
    $exitCode = $LASTEXITCODE

    $output | Tee-Object -FilePath $LogFile -Append

    if ($exitCode -ne 0) {
        throw "$StepName failed with exit code $exitCode"
    }
}

Write-Log "VT-RAP automation started"

try {
    Invoke-LoggedCommand `
        -StepName "Running full refresh" `
        -Executable $PythonExe `
        -Arguments @("scripts\run_full_refresh.py")

    Invoke-LoggedCommand `
        -StepName "Running tests" `
        -Executable $PythonExe `
        -Arguments @("-m", "pytest")

    Write-Log "Opening Streamlit dashboard"

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd `"$ProjectRoot`"; & `"$PythonExe`" -m streamlit run app\streamlit_app_v2.py"
    )

    Write-Log "VT-RAP automation completed successfully"
}
catch {
    Write-Log "VT-RAP automation failed"
    Write-Log $_.Exception.Message
    exit 1
}