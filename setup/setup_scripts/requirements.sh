#!/usr/bin/env bash

# Code from GOAD project : https://github.com/Orange-Cyberdefense/GOAD/blob/main/scripts/check.sh
# and from DetectionLab : https://github.com/clong/DetectionLab


ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)


install_vbox(){
    #install requirements
    sudo apt-get install build-essential gcc make perl dkms -y 
    sudo apt install virtualbox -y 
    # may solve erros after installation
    # sudo /sbin/vboxconfig 
}

install_vagrant(){
    wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg 
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list 
    sudo apt update && sudo apt install vagrant 
}

# Returns 0 if not installed or 1 if installed
check_virtualbox_installed() {
  if ! which VBoxManage >/dev/null; then
    (echo >&2 "${ERROR} VBoxManage was not found in your PATH.")
    (echo >&2 "${ERROR} Trying to install vbox...")
    install_vbox
    if ! which VBoxManage >/dev/null; then
        (echo >&2 "${ERROR} Vbox installation failed")
        (echo >&2 "${ERROR} Correct this by installing virtualbox manually")
        exit 1
    else
        (echo >&2 "${GOODTOGO} virtualbox is installed")
    fi
  else
    (echo >&2 "${GOODTOGO} virtualbox is installed")
  fi
}

check_vagrant_path() {
  if ! which vagrant >/dev/null; then
    (echo >&2 "${ERROR} Vagrant was not found in your PATH.")
    (echo >&2 "${ERROR} Trying to install vagrant...")
    install_vagrant
    if ! which vagrant >/dev/null; then
        (echo >&2 "${ERROR} Vagrant installation failed")
        (echo >&2 "${ERROR} Correct this by installing vagrant manually")
        exit 1
    else
        (echo >&2 "${GOODTOGO} Vagrant was found in your PATH")
    fi
  else
    (echo >&2 "${GOODTOGO} Vagrant was found in your PATH")

    # Ensure Vagrant >= 2.2.9
    # https://unix.stackexchange.com/a/285928
    VAGRANT_VERSION="$(vagrant --version | cut -d ' ' -f 2)"
    REQUIRED_VERSION="2.2.9"
    # If the version of Vagrant is not greater or equal to the required version
    if ! [ "$(printf '%s\n' "$REQUIRED_VERSION" "$VAGRANT_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        (echo >&2 "${ERROR} WARNING: It is highly recommended to use Vagrant $REQUIRED_VERSION or above before continuing")
    else 
        (echo >&2 "${GOODTOGO} Your version of Vagrant ($VAGRANT_VERSION) is supported")
    fi
  fi
}

check_vagrant_reload_plugin() {
  # Ensure the vagrant-reload plugin is installed
  VAGRANT_RELOAD_PLUGIN_INSTALLED=$(vagrant plugin list | grep -c 'vagrant-reload')
  if [ "$VAGRANT_RELOAD_PLUGIN_INSTALLED" != "1" ]; then
    (echo >&2 "${ERROR} The vagrant-reload plugin is required and was not found. This script will attempt to install it now.")
    if ! $(which vagrant) plugin install "vagrant-reload"; then
      (echo >&2 "Unable to install the vagrant-reload plugin. Please try to do so manually and re-run this script.")
      exit 1
    else 
      (echo >&2 "${GOODTOGO} The vagrant-reload plugin was successfully installed!")
    fi
  else
    (echo >&2 "${GOODTOGO} The vagrant-reload plugin is currently installed")
  fi
}

# Check available disk space. Recommend 50GB free, warn if less.
check_disk_free_space() {
  FREE_DISK_SPACE=$(df -m "$HOME" | tr -s ' ' | grep '/' | cut -d ' ' -f 4)
  if [ "$FREE_DISK_SPACE" -lt $DISK_REQ ]; then
    (echo >&2 "${INFO} Warning: You appear to have less than $(($DISK_REQ / 1000))GB of HDD space free on your primary partition. If you are using a separate parition, you may ignore this warning.")
  else
    (echo >&2 "${GOODTOGO} You have more than $(($DISK_REQ / 1000))GB of free space on your primary partition")
  fi
}

check_ram_space() {
  RAM_SPACE=$(free|tr -s ' '|grep Mem|cut -d ' ' -f 2)
  if [ "$RAM_SPACE" -lt $RAM_REQ ]; then
    (echo >&2 "${INFO} Warning: You appear to have less than $(($RAM_REQ / 1024 /1024))GB of RAM on your disk, perform issues may occur.\n")
  else
    (echo >&2 "${GOODTOGO} You have more than $(($RAM_REQ / 1024 /1024))GB of ram")
  fi
}

check_docker(){
    if ! which docker >/dev/null; then
        (echo >&2 "${ERROR} Docker is not installed")
        (echo >&2 "${ERROR} Correct this by installing docker manually")
        exit 1
    else
        (echo >&2 "${GOODTOGO} Docker was found in your PATH")
    fi
    # check docker compose
    if ! docker compose >/dev/null; then
        (echo >&2 "${ERROR} Docker compose is not installed")
        (echo >&2 "${ERROR} Correct this by installing docker compose manually")
        exit 1
    else
        (echo >&2 "${GOODTOGO} Docker compose was found in your PATH")
    fi 
}

check_vbox(){
    # https://stackoverflow.com/questions/59895/getting-the-source-directory-of-a-bash-script-from-within
    check_virtualbox_installed
    check_vagrant_path
    check_vagrant_reload_plugin
    check_disk_free_space
    check_ram_space
}

check_docker_desktop_installed() {
  script='
  $dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue;
  if ($dockerProcess) {
      Write-Host "Docker Desktop is installed and running.";
  } else {
      Write-Host "Docker Desktop is not installed or not running.";
  }
  '
  
  output=$(powershell.exe -Command "$script")
  
  expected_output="Docker Desktop is installed and running."

  if [ "$output" != "$expected_output" ]; then
      (echo >&2 "${WARNING} Docker Desktop is not installed or not running.")
      (echo >&2 "${WARNING} Details :")
      (echo >&2 "$output")
      return 1
  else
      (echo >&2 "${GOODTOGO} Docker Desktop is installed and running.")
  fi
}

check_docker_windows_containers() {
  script='
  $osType = docker info --format "{{.OSType}}";
  if ($osType -eq "windows") {
      Write-Host "Docker is configured to build Windows containers.";
  } elseif ($osType -eq "linux") {
      Write-Host "Docker is configured to build Linux containers.";
  } else {
      Write-Host "Could not determine Docker'"'"'s container mode.";
  }
  '
  output=$(powershell.exe -Command "$script")
  
  expected_output="Docker is configured to build Windows containers."

  if [ "$output" != "$expected_output" ]; then
      (echo >&2 "${ERROR} Docker is not configured to build Windows containers.")
      (echo >&2 "${ERROR} Actual details :")
      (echo >&2 "$output")
      return 1
  else
      (echo >&2 "${GOODTOGO} Docker is configured to build Windows containers.")
  fi
}


main() {
    check_docker 
    # Check vbox & vagrant only for local installation
    if [ "$1" = vbox ]; then
        check_vbox
    elif [ "$1" = docker_desktop ]; then
        # Add ps1 to path
        WINDOWS_POWERSHELL_PATH="/mnt/c/Windows/System32/WindowsPowerShell/v1.0"
        if ! echo $PATH | grep -q "$WINDOWS_POWERSHELL_PATH"; then
            export PATH="$PATH:$WINDOWS_POWERSHELL_PATH"
        fi
        check_docker_desktop_installed
        check_docker_windows_containers
    fi
}

main $1 # First arg is used extend checks to vbox/vagrant
exit 0