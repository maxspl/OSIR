Master Setup
============

The recommended option is to use the unified launcher ``osir-launcher.py`` to run the interactive setup and start the MASTER component.

Interactive setup (recommended)
-------------------------------

.. code-block:: bash

    cd OSIR
    python3 osir-launcher.py start master

To see available launcher commands:

.. code-block:: bash

    python3 osir-launcher.py -h

To see options for the start command:

.. code-block:: bash

    python3 osir-launcher.py start -h

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

**Path**: ``OSIR/setup/conf/master.yml``

**Content**:

.. code-block:: yaml

    splunk: # Parameters of local (self deployed by master) or external (deployed by yourself) Splunk server
      location: {splunk_location} # external (deployed by yourself) or local (self deployed by master)
      user: {splunk_user}
      password: {splunk_password}
      port: {splunk_port} # default is 8000
      mport: {splunk_mport} # default is 8089
      ssl: {splunk_ssl} # True or False
      local_splunk: # what to do with Splunk data if a previous installation has been done
        previous_data: erase # possible values: erase, keep, stop
      remote_splunk:
        host: {splunk_remote_splunk_host} # IP or FQDN if external Splunk

Replace the placeholders (e.g., ``{splunk_location}``, ``{splunk_user}``) with the actual values for your setup.

.. note::
   Splunk parameters are not used and are not tested during the setup. They are used afterwards by processing modules.

Example Usage
-------------

To start MASTER while reusing the detected configuration:

.. code-block:: bash

    python3 osir-launcher.py start master --config

