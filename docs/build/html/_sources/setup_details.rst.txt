
Master setup in details 
=======================

The basic option is to use **make** command to start interactive setup.

.. code-block:: bash

    cd OSIR
    make master

To access more setup option, run the setup script for the master directory.

.. code-block:: bash

    cd OSIR/setup/master
    sudo ./master_setup.sh

Usage:

.. code-block:: console

    Usage: ./master_setup.sh [-d] [-h] [-c]
    Options:
      -d  Enable debug mode
      -h  Show this help message
      -c  Setup master from config file. Default is interactive

Options Explained
-----------------

- **-d**: Enable debug mode. This option provides more detailed output for troubleshooting.
- **-h**: Show the help message. Use this option to see all available options and their descriptions.
- **-c**: Setup master from a configuration file. If this option is not used, the script runs in interactive mode by default.

Using a Configuration File
--------------------------

Instead of running the script in interactive mode, you can use a configuration file. Here is an example of a configuration file that can be used:

**Path**: `OSIR/setup/conf/master.yanl`

**Content**:

.. code-block:: yaml

    splunk: # Paramters of local (self deployed by master) or external (deployed by yourself) Splunk server
      location: {splunk_location} # external (deployed by yourself or local (self deployed by master)
      user: {splunk_user}
      password: {splunk_password}
      port: {splunk_port} # default is 8000
      mport: {splunk_mport} # default is 8089
      ssl: {splunk_ssl} # True or False
      local_splunk: # what to do with Splunk data if a previous installation has been done
        previous_data: erase # possible values: erase, keep, stop 
      remote_splunk: 
        host: {splunk_remote_splunk_host} # IP or FQDN if external Splunk

Replace the placeholders (e.g., `{splunk_location}`, `{splunk_user}`) with the actual values for your setup.

.. note:: Splunk parameters are not used and are not tested during the setup. They are used afterwards by processing modules.

Example Usage
-------------

To run the script with the configuration file, use the following command:

.. code-block:: bash

    sudo ./master_setup.sh -c 

Agent setup in details 
======================

The basic option is to use **make** command to start interactive setup.

.. code-block:: bash

    cd OSIR
    make agent

To access more setup option, run the setup script for the master directory.

.. code-block:: bash

    cd OSIR/setup/agent
    sudo ./agent_setup.sh

Usage:

.. code-block:: console

    Usage: ./agent_setup.sh [-d] [-h] [-c]
    Options:
      -d  Enable debug mode
      -h  Show this help message
      -c  Setup agent from config file. Default is interactive

Options Explained
-----------------

- **-d**: Enable debug mode. This option provides more detailed output for troubleshooting.
- **-h**: Show the help message. Use this option to see all available options and their descriptions.
- **-c**: Setup agent from a configuration file. If this option is not used, the script runs in interactive mode by default.

Using a Configuration File
--------------------------

Instead of running the script in interactive mode, you can use a configuration file. Here is an example of a configuration file that can be used:

**Path**: `OSIR/setup/conf/agent.yaml`

**Content**:

.. code-block:: yaml

    master:
        host: {master_host} # If windows machine is remote but master and agent are on the same host, specify the IP used by Windows IP to connect master 
    splunk: # Paramters of local (self deployed by master) or external (deployed by yourself) Splunk server
        host: {splunk_host}
        user: {splunk_user}
        password: {splunk_password}
        port: {splunk_port} # default is 8000
        mport: {splunk_mport} # default is 8089
        ssl: {splunk_ssl} # True or False
    windows_box:
        location: {windows_box_location} # external (deployed by yourself) or local (self deployed by master)
        cores: {windows_box_cores} # Number of cores of the windows box, to adapt the number of concurrent tasks
        remote_box: # if external (deployed by yourself) windows box
            host: {windows_box_remote_box_host} # IP or FQDN
            user: {windows_box_remote_box_user} # admin user 
            password: {windows_box_remote_box_password}
            custom_mountpoint: {windows_box_remote_box_custom_mountpoint} # Drive letter (Ex. D)

Replace the placeholders (e.g., `{splunk_location}`, `{splunk_user}`) with the actual values for your setup.

.. note:: Splunk parameters are not used and are not tested during the setup. They are used afterwards by processing modules.

.. warning:: If using your own Windows box, Winrm must enabled and user provided must be admin. Internet access is also required to setup tools.

Example Usage
-------------

To run the script with the configuration file, use the following command:

.. code-block:: bash

    sudo ./agent_setup.sh -c 