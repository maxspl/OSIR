# Define the log file
$logFile = "C:\setup_osir.log"

# Function to log messages
function Log {
    param (
        [string]$message
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $message" | Out-File -FilePath $logFile -Append
}

# Ensure the directory exists
$path = "C:\OSIR"
Log "Checking if directory $path exists."
if (-not (Test-Path -Path $path)) {
    Log "Directory $path does not exist. Creating it."
    New-Item -Path $path -ItemType Directory | Out-Null
}

# Add exclusion for C:\OSIR
Log "Adding exclusion for directory $path in Windows Defender."
Add-MpPreference -ExclusionPath $path 2>&1 | Out-File -FilePath $logFile -Append

# Define the script content
$scriptContent = 'Set-MpPreference -DisableRealtimeMonitoring $true ; Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False'

# Write the content to the script file
$scriptFile = "$path\script.ps1"
Log "Creating script file at $scriptFile with predefined content."
Set-Content -Path $scriptFile -Value $scriptContent

# Run the script
Log "Executing script $scriptFile."
Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -File $scriptFile" -Wait 2>&1 | Out-File -FilePath $logFile -Append

# Delete the script file after execution
Log "Deleting script file $scriptFile."
remove-Item -Path $scriptFile -Force

# Install Chocolatey
Log "Installing Chocolatey."
# Invoke-Expression "& { $(Invoke-RestMethod 'https://aka.ms/install-powershell.ps1') } -AddToPath" 2>&1 | Out-File -FilePath $logFile -Append
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1')) 2>&1 | Out-File -FilePath $logFile -Append

# Enable too long paths
Log "Enabling support for long paths."
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force 2>&1 | Out-File -FilePath $logFile -Append

# Change execution policy
Log "Setting execution policy to unrestricted."
Set-ExecutionPolicy unrestricted -scope Process -Force

# Create custom tools directory
$bin_dir = "C:\OSIR\bin"
Log "Creating custom tools directory at $bin_dir."
New-Item -ItemType Directory -Path $bin_dir -Force

# Enable unsecure SMB share access
Log "Enabling insecure SMB share access."
reg add HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters /v AllowInsecureGuestAuth /t reg_dword /d 00000001 /f 2>&1 | Out-File -FilePath $logFile -Append

# Set local bin source based on a file only present in the docker
if (Test-Path "C:\Windows\Temp\local_host_identifier.OSIR") {
    Log "Detected local host identifier. Using local source for bin directory."
    $OSIR_path = Get-Content "C:\Windows\Temp\local_host_identifier.OSIR"
    $bin_dir_src = "$OSIR_path\share\src\bin\*"
} else {
    Log "Using remote source for bin directory."
    $bin_dir_src = "\\master_host\share\src\bin\*"
}

# Copy all tools
Log "Copying tools from $bin_dir_src to $bin_dir."
Copy-Item -Path $bin_dir_src -Destination $bin_dir -Recurse 2>&1 | Out-File -FilePath $logFile -Append

# Download and extract EZ tools
$zipUrl = "https://f001.backblazeb2.com/file/EricZimmermanTools/Get-ZimmermanTools.zip"
Log "Downloading EZ tools from $zipUrl."
Invoke-WebRequest -Uri $zipUrl -OutFile "$env:TEMP\Get-ZimmermanTools.zip" 2>&1 | Out-File -FilePath $logFile -Append
Log "Extracting EZ tools to $bin_dir."
Expand-Archive -Path "$env:TEMP\Get-ZimmermanTools.zip" -DestinationPath $bin_dir -Force
Log "Running Get-ZimmermanTools script."
& "$bin_dir\Get-ZimmermanTools.ps1" -Dest $bin_dir 2>&1 | Out-File -FilePath $logFile -Append

# Install dependencies
Log "Installing .NET 6.0 desktop runtime and Python 3.11."
choco install dotnet-6.0-desktopruntime -y 2>&1 | Out-File -FilePath $logFile -Append
choco install python311 -y 2>&1 | Out-File -FilePath $logFile -Append

# Reload path
Log "Reloading PATH environment variable."
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Copy Python binary
$python_exe = $(Get-Command python.exe).Source
if (Test-Path -Path $python_exe) {
    $destination_path = Join-Path -Path $bin_dir -ChildPath "python.exe"
    Log "Copying Python executable from $python_exe to $destination_path."
    Copy-Item -Path $python_exe -Destination $destination_path -Force
} else {
    Log "Python executable not found in the PATH. Operation not completed."
}

# Install Python requirements
if (Test-Path "C:\Windows\Temp\local_host_identifier.OSIR") {
    Log "Installing Python requirements from local path."
    $python_req = "$OSIR_path\share\src\dependencies\requirements.txt"
} else {
    Log "Installing Python requirements from remote path."
    $python_req = "\\master_host\share\src\dependencies\requirements.txt"
}
python -m pip install -r $python_req 2>&1 | Out-File -FilePath $logFile -Append

# Download Hindsight
$Url = "https://github.com/obsidianforensics/hindsight/releases/download/v20-23.03/hindsight.exe"
Log "Downloading Hindsight from $Url to $bin_dir."
Invoke-WebRequest -Uri $Url -OutFile "$bin_dir\hindsight.exe" 2>&1 | Out-File -FilePath $logFile -Append

# Update RECmd batch files
Log "Updating RECmd batch files."
C:\OSIR\bin\net6\RECmd\RECmd.exe --sync 2>&1 | Out-File -FilePath $logFile -Append

Log "Setup process completed successfully."
