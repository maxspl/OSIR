winrm quickconfig -q -force
Start-Service winrm
Start-Sleep -Seconds 10
winrm set winrm/config/service/Auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
set winrm/config/winrs '@{MaxMemoryPerShellMB="0"};'