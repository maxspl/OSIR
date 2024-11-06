import winrm
import requests.exceptions
import re


class vagrantfile:
    def __init__(self, path):
        self.path = path
        self.parsing_status, self.commands = self.parse_Vagrantfile()
        if self.parsing_status:
            print("Successful Vagrantfile parsing")

        else:
            print("Failed Vagrantfile parsing")
            exit(1) 

    def parse_Vagrantfile(self):
        """
            Extract powershell commands from a Vagrantfile.

            Parameters:
                Vagrantfile (str): Vagrantfile path

            Returns:
                commands_list_filtered (list): list of ps1 commands

        """
        try:
            Vagrantfile_content = open(self.path, 'r').read()
        except Exception as e:
            return False, f"Cannot read Vagrantfile. Error : {str(e)}" 
        # Capture all powershell commands
        shell_commands = re.findall(r'<<-SHELL(.*?)SHELL', Vagrantfile_content, re.DOTALL)
        # Make a single list containing all commands
        commands_list = [line.strip() for command in shell_commands for line in command.split('\n')]
        # Exclude lines containing "#only local", commented lines, and remove empty lines
        commands_list_filtered = [line for line in commands_list if line.strip() and not line.strip().startswith("#") and "#only local" not in line]
        return True, commands_list_filtered


class box:
    def __init__(self, host, username, password, mount_point="C:", port=5985):
        self.host = host
        self.username = username
        self.password = password
        self.mount_point = mount_point
        self.port = port
        if self.mount_point != "C:" and not self.is_mount_point():
            print(f"{mount_point} is not a mount point. Ex: D:")
            exit(1)
        self.winrm_host = f"http://{self.host}:{self.port}/wsman"
      
    def exec_winrm(self, cmd):
        """
            Exec winrm powershell command on the specified host.

            Parameters:
                cmd (str): Powershell command to run

            Returns:
                True if the connection is working
                False if not
        """
        try:
            session = winrm.Session(self.winrm_host, auth=(self.username, self.password))
            r = session.run_ps(cmd)

            if r.status_code == 0:
                return True, r.std_out + r.std_err  
            else:
                return False, r.std_err
        except requests.exceptions.ConnectionError:
            return False, "Connection refused error occurred. Please check the connection settings."
        except Exception as e:
            return False, f"Unidentified error: Error : {str(e)}"

    def exec_winrm_script(self, script_path, master_host, cmd=None):
        """
            Exec powershell script on the specified host.

            Parameters:
                script_path (str): Path of the powershell script to run

            Returns:
                True if the connection is working
                False if not
        """
        try:
            with open(script_path, "r") as f:
                script_content = f.read()
            if cmd is not None:
                script_content = cmd + "\n" + script_content
            script_content = script_content.replace("master_host", master_host)
            script_content = script_content.replace("C:", self.mount_point)
            # print(script_content)
            # script_content = "ls"
            
            cmd = """
            # Load script from env-vars
            . ([ScriptBlock]::Create($Env:WINRM_SCRIPT))
            """
            from base64 import b64encode
            encoded_cmd = b64encode(cmd.encode('utf_16_le')).decode('ascii')

            p = winrm.protocol.Protocol(self.winrm_host, username=self.username, password=self.password)

            # Load script to env vars.
            shell = p.open_shell(env_vars=dict(WINRM_SCRIPT=script_content))
            command = p.run_command(shell, "powershell -EncodedCommand {}".format(encoded_cmd))

            r = winrm.Response(p.get_command_output(shell, command))

            p.cleanup_command(shell, command)
            p.close_shell(shell)

            # session = winrm.Session(self.winrm_host, auth=(self.username, self.password))
            # r = session.run_ps(script_content)
            if r.status_code == 0:
                return True, r.std_out + r.std_err
            else:
                return False, r.std_err
        except requests.exceptions.ConnectionError:
            return False, "Connection refused error occurred. Please check the connection settings."
        except Exception as e:
            return False, f"Unidentified error: Error : {str(e)}"
        
    def is_mount_point(self):
        # Define a regular expression pattern to match disk mount points like "C:", "D:", etc.
        pattern = r'^[A-Za-z]:$'
        # Use the re.match() function to check if the variable matches the pattern
        if re.match(pattern, self.mount_point):
            return True
        else:
            return False
