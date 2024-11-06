import winrm
import requests.exceptions


def exec_winrm(cmd):
    """
        Exec winrm powershell command on the specified host.

        Parameters:
            cmd (str): Powershell command to run

        Returns:
            True if the connection is working
            False if not
    """
    try:
        host = "http://192.168.1.77:5985/wsman"
        username = "vagrant"
        password = 'vagrant'
        session = winrm.Session(host, auth=(username, password))
        r = session.run_ps(cmd)

        if r.status_code == 0:
            return True, r.std_out + r.std_err  
        else:
            return False, r.std_err
    except requests.exceptions.ConnectionError:
        return False, "Connection refused error occurred. Please check the connection settings."
    except Exception as e:
        return False, f"Unidentified error: Error : {str(e)}"
    
    
status, stdout = exec_winrm("ipconfig")
print(stdout)

