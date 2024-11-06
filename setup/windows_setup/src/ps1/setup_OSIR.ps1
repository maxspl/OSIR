# Ensure the directory exists
$path = "C:\OSIR"
if (-not (Test-Path -Path $path)) {
    New-Item -Path $path -ItemType Directory | Out-Null
}

# Add exclusion for C:\OSIR
Add-MpPreference -ExclusionPath "C:\OSIR"

# Define the script content
$scriptContent = 'Set-MpPreference -DisableRealtimeMonitoring $true ; Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False'

# Write the content to the script file
$scriptFile = "$path\script.ps1"
Set-Content -Path $scriptFile -Value $scriptContent

# Run the script
Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -File $scriptFile" -Wait

# Delete the script file after execution
Remove-Item -Path $scriptFile -Force

# Optionally, remove the directory if empty
if ((Get-ChildItem -Path $path).Count -eq 0) {
    Remove-Item -Path $path -Force
}

# # Install Chocolatey
Invoke-Expression "& { $(Invoke-RestMethod 'https://aka.ms/install-powershell.ps1') } -AddToPath"
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
# # Enable too long paths
New-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
# # Change exec policy
Set-ExecutionPolicy unrestricted  -scope Process -Force

# Create custom tools directory
$bin_dir = "C:\\OSIR\\bin"
New-Item -ItemType Directory -Path $bin_dir -Force

# Enable unsecure smb share access - should be already applied by check_smb
reg add HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters /v AllowInsecureGuestAuth /t reg_dword /d 00000001 /f
# Set local bin source based on a file only present in the docker

if (Test-Path "C:\Windows\Temp\local_host_identifier.OSIR") {
    $OSIR_path = Get-Content "C:\Windows\Temp\local_host_identifier.OSIR"
    $bin_dir_src = "$OSIR_path\share\src\bin\*"
} else {
    $bin_dir_src = "\\master_host\share\src\bin\*"
}

# Copy all tools
Copy-Item -Path $bin_dir_src -Destination $bin_dir
# --- Download EZ tools
# Download zip file
$zipUrl = "https://f001.backblazeb2.com/file/EricZimmermanTools/Get-ZimmermanTools.zip"
Invoke-WebRequest -Uri $zipUrl -OutFile "$env:TEMP\Get-ZimmermanTools.zip"
# Extract the contents of the zip file
Expand-Archive -Path "$env:TEMP\Get-ZimmermanTools.zip" -DestinationPath $bin_dir -Force
# Run Get-ZimmermanTools with the specified options
& "$bin_dir\\Get-ZimmermanTools.ps1" -Dest $bin_dir
# Install dotnet 6.0
choco install dotnet-6.0-desktopruntime -y
# Install python311
choco install python311 -y

# Reload path
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") 

# Set python requirements based on a file only present on a Windows host (vs VM)
if (Test-Path "C:\Windows\Temp\local_host_identifier.OSIR") {
    $python_req = "$OSIR_path\share\src\dependencies\requirements.txt"
} else {
    $python_req = "\\master_host\share\src\dependencies\requirements.txt"
}

#Install python requirements
python -m pip install -r $python_req

# Download Hindsight
$Url = "https://github.com/obsidianforensics/hindsight/releases/download/v20-23.03/hindsight.exe"
Invoke-WebRequest -Uri $Url -OutFile "$bin_dir\hindsight.exe"

# Update recmd batch files
C:\OSIR\bin\net6\RECmd\RECmd.exe --sync