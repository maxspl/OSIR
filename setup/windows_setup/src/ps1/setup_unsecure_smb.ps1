# Configure unsecure smb access
$path = "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters"
$name = "AllowInsecureGuestAuth"
$desiredValue = 0x1  # This is hexadecimal for 1

# Check if the path exists and read the value if it does
if (Test-Path $path) {
    $currentValue = (Get-ItemProperty -Path $path -Name $name -ErrorAction SilentlyContinue).$name
    if ($currentValue -ne $desiredValue) {
        # The value is not what we want, change it
        reg add HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters /v AllowInsecureGuestAuth /t reg_dword /d 00000001 /f

        Write-Host "Registry key value has been set/updated."
    } else {
        Write-Host "Registry key value is already set to the desired value. No action taken."
    }
} else {
    # The path does not exist, add the key
    reg add HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters /v AllowInsecureGuestAuth /t reg_dword /d 00000001 /f
    Write-Host "Registry key has been added as it did not exist."
}
