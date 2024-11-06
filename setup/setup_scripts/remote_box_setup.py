import utils.winrm_utils


def check_winrm(host, username, password, mount_point="C:", port=5985):
    """
        Run a winrm command to ccheck if winrm is working.
        Increase MaxMemoryPerShellMB for winrm.
        Check if OSIR has already been configured on the windows host.

        Parameters:
            host (str): IP address or FQDN of the windows host
            username (str): Username to use for winrm connection
            password (str): Password to use for winrm connection
            mount_point (str): custom moint point of the Windows box to install tools
        Returns:
    """
    box = utils.winrm_utils.box(host, username, password, mount_point, port=port)
    # Check if winrm is working
    status, output = box.exec_winrm("whoami")
    if status:
        print("Successful winrm command: check winrm")
        print("winrm stdout: ", str(output).replace('\\r\\n', '\n'))

    else:
        print("Failed winrm command: check winrm.")
        print("winrm stderr: ", str(output).replace('\\r\\n', '\n'))
        exit(1)

    # Increase MaxMemoryPerShellMB
    cmd = "Set-Item -Path WSMan:\\localhost\\Shell\\MaxMemoryPerShellMB -Value 65536"
    status, output = box.exec_winrm(cmd)
    if status:
        print("Successful winrm command: increase MaxMemoryPerShellMB")
        print("winrm stdout: ", str(output).replace('\\r\\n', '\n'))

    else:
        print("Failed winrm command: increase MaxMemoryPerShellMB")
        print("winrm stderr: ", str(output).replace('\\r\\n', '\n'))
        exit(1)

    # Check if OSIR already configured on the host
    status, output = box.exec_winrm(f"Test-Path -Path '{mount_point}\\OSIR'")
    if status:
        print("Successful winrm command: check OSIR installation")
        print("winrm stdout: ", str(output).replace('\\r\\n', '\n'))

    else:
        print("Failed winrm command: check OSIR installation")
        print("winrm stderr: ", str(output).replace('\\r\\n', '\n'))
        exit(1)


def check_smb(host, username, password, ps1_script_path, master_host):
    """
        Check if smb share can be accessed.

        Parameters:
            host (str): IP address or FQDN of the windows host
            username (str): Username to use for winrm connection
            password (str): Password to use for winrm connection
            master_host (str): IP or FQDN of the master host
        Returns:

    """
    # Check if SMB share of master can be accessed

    box = utils.winrm_utils.box(host, username, password)
    if master_host == "127.0.0.1" or master_host == "host.docker.internal":
        master_host = "10.0.2.2"  # Gateway IP set by vbox        

    # ps1_script_path = "/OSIR/setup/windows_setup/src/ps1/setup_unsecure_smb.ps1" 
    # Enable unsecure smb share access if not already set
    status, output = box.exec_winrm_script(ps1_script_path, master_host)
    if status:
        print(f"Successful winrm script execution: {ps1_script_path}")
        print("winrm stdout: ", str(output).replace('\\n', '\n'))

    else:
        print(f"Failed winrm command: {ps1_script_path}")
        print("winrm stderr: ", str(output).replace('\\r\\n', '\n'))
        exit(1)

    # check if we can ls the smb share
    cmd = f"ls \\\\{master_host}\\share\\"
    status, output = box.exec_winrm(cmd)
    if status and "src" in str(output):
        print("Successful winrm command: check smb list share files")
        print("winrm stdout: ", str(output).replace('\\r\\n', '\n'))

    else:
        print("Failed winrm command: check smb list share files")
        print("winrm stderr: ", str(output).replace('\\r\\n', '\n'))
        exit(1)


def setup_OSIR(host, username, password, ps1_script_path, master_host, mount_point="C:"):
    """
        Run powershell script on the specified host

        Parameters:
            host (str): IP address or FQDN of the windows host
            username (str): Username to use for winrm connection
            password (str): Password to use for winrm connection
            ps1_script_path (str): Path of the script to run
            mount_point (str): custom moint point of the Windows box to install tools
        Returns:
    """
    box = utils.winrm_utils.box(host, username, password, mount_point)
    if master_host == "127.0.0.1" or master_host == "host.docker.internal":
        master_host = "10.0.2.2"  # Gateway IP set by vbox
    # Append this line to the script to setup the smb share
    # cmd = f"New-SmbMapping -LocalPath R: -RemotePath \\\\{master_host}\\share -UserName {username} -Password '{password}'  -Persistent 1"
    # Run installation script

    status, output = box.exec_winrm_script(ps1_script_path, master_host)
    if status:
        print(f"Successful winrm script execution: {ps1_script_path}")
        print("winrm stdout: ", str(output).replace('\\n', '\n'))

    else:
        print(f"Failed winrm command: {ps1_script_path}")
        print("winrm stderr: ", str(output).replace('\\r\\n', '\n'))
        exit(1)


# check_winrm("127.0.0.1", "vagrant", "vagrant", "C:")
# check_smb("127.0.0.1", "vagrant", "vagrant", "127.0.0.1")
# configure_remote_box("127.0.0.1", "vagrant", "vagrant", "/opt/OSIR/setup/windows_setup/Vagrantfile", "C:")
# setup_smb("127.0.0.1", "vagrant", "vagrant", "/opt/perso/OSIR_main/OSIR/setup/windows_setup/src/ps1/setup_smb.ps1", "C:")
# setup_OSIR("127.0.0.1", "vagrant", "vagrant", "/opt/perso/OSIR_main/OSIR/setup/windows_setup/src/ps1/setup_OSIR.ps1", "127.0.0.1", mount_point="C:")
