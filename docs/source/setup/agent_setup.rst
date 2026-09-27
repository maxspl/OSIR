Agent Setup
===========

The recommended option is to use the unified launcher ``osir-launcher.py`` to run the interactive setup and start the AGENT component.

Interactive setup (recommended)
-------------------------------

.. code-block:: bash

    cd OSIR
    python3 osir-launcher.py start agent

Options Explained
-----------------

- **--offline**: Run in offline mode (use offline compose/services when available).
- **--debug**: Enable verbose output for troubleshooting.
- **--config**: Use an existing configuration file instead of prompting interactively.
- **--attach**: Attach to container output (interactive) instead of starting in background.
- **--debug-shell**: Start the container with a shell entrypoint (development/debug only).

Using a Configuration File
--------------------------

Instead of running the setup in interactive mode, you can reuse an existing configuration file.

**Path**: ``OSIR/setup/conf/agent.yml``

**Content**:

.. code-block:: yaml

    master:
        host: {master_host} # If windows machine is remote but master and agent are on the same host, specify the IP used by Windows to connect to master
    splunk: # Parameters of local (self deployed by master) or external (deployed by yourself) Splunk server
        host: {splunk_host}
        user: {splunk_user}
        password: {splunk_password}
        port: {splunk_port} # default is 8000
        mport: {splunk_mport} # default is 8089
        ssl: {splunk_ssl} # True or False
    windows_box:
        location: {windows_box_location} # external (deployed by yourself) or local
        cores: {windows_box_cores} # Number of cores of the windows box, to adapt the number of concurrent tasks
        remote_box: # if external (deployed by yourself) windows box
            host: {windows_box_remote_box_host} # IP or FQDN
            user: {windows_box_remote_box_user} # admin user
            password: {windows_box_remote_box_password}
            custom_mountpoint: {windows_box_remote_box_custom_mountpoint} # Drive letter (Ex. D)

Replace the placeholders (e.g., ``{splunk_host}``, ``{splunk_user}``) with the actual values for your setup.

.. note::
   Splunk parameters are not used and are not tested during the setup. They are used afterwards by processing modules.

.. warning::
   If using your own Windows box, WinRM must be enabled and the user provided must be admin.
   Internet access is also required to setup tools.

Example Usage
-------------

To start AGENT while reusing the detected configuration:

.. code-block:: bash

    python3 osir-launcher.py start agent --config

