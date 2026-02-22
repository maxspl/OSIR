
Master setup in details
=======================

The recommended option is to use the unified launcher ``osir-launcher.py`` to run the interactive setup and start the MASTER component.

Interactive setup (recommended)
-------------------------------

.. code-block:: bash

    cd OSIR
    sudo python3 osir-launcher.py start master

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

    sudo python3 osir-launcher.py start master --config
Agent setup in details
======================

The recommended option is to use the unified launcher ``osir-launcher.py`` to run the interactive setup and start the AGENT component.

Interactive setup (recommended)
-------------------------------

.. code-block:: bash

    cd OSIR
    sudo python3 osir-launcher.py start agent

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

    sudo python3 osir-launcher.py start agent --config

Developer mode (Module development)
===================================

When developing OSIR modules, it is often useful to:

- Start or stop OSIR quickly
- Launch OSIR manually inside the container
- Watch logs in real time
- Restart only the OSIR process without recreating containers

The launcher provides a **developer mode** using the options:

- ``--attach``
- ``--debug-shell``

This mode starts containers with a shell entrypoint instead of
launching OSIR automatically.

.. warning::
   This mode is intended for development and debugging only.
   Normal users should use ``start all`` without debug options.

Recommended workflow
********************

It is recommended to use **two terminals**.

Terminal 1: MASTER
----------------------------------------

Start MASTER in developer mode:

.. code-block:: bash

    sudo python3 osir-launcher.py start master --attach --debug-shell

What happens:

- Existing configuration is reused
- Docker compose is temporarily patched
- The container starts with ``bash`` instead of ``OSIR.py``
- You get an interactive shell inside the container

Example message:

.. code-block:: console

    Container started with bash as entrypoint.
    Now you have to run manually inside the shell:
        OSIR.py --web

Inside the container shell, start OSIR manually:

.. code-block:: bash

    OSIR.py --web

You will now see MASTER (web) logs live in this terminal.
This is ideal when developing or debugging modules.

Terminal 2: AGENT
---------------------------------------

Start AGENT in developer mode:

.. code-block:: bash

    sudo python3 osir-launcher.py start agent --attach --debug-shell

Inside the container shell, launch:

.. code-block:: bash

    OSIR.py --agent

You will now see AGENT logs live in this terminal.
This allows you to:

- Observe processing logs live
- Restart the agent process quickly
- Test modules without rebuilding containers

Why use developer mode?
***********************

Developer mode is useful when:

- Creating or modifying OSIR modules
- Debugging API or processing behavior
- Watching Streamlit or backend logs live
- Restarting OSIR quickly after code changes

Instead of restarting all containers, you only restart:

.. code-block:: bash

    OSIR.py --web
    # or
    OSIR.py --agent

This significantly speeds up development cycles.

The goal is to keep:

- Terminal 1 for MASTER (web) logs
- Terminal 2 for AGENT logs

Air Gap setup
=============

OSIR supports deployment in **air-gapped environments** (no internet access).
This is done by exporting Docker images from an online host and loading them
on the offline host.

Overview
--------

The workflow is:

1. Prepare OSIR on an **internet-connected host**
2. Export Docker images using the launcher
3. Transfer the offline release to the air-gapped host
4. Load images and start OSIR in offline mode

Step 1 — Prepare OSIR on an online host
---------------------------------------

Setup MASTER and AGENT normally on a machine with internet access:

.. code-block:: bash

    cd OSIR
    sudo python3 osir-launcher.py start all

This ensures all required images are built locally.


Step 2 — Export Docker images
------------------------------

Use the launcher to generate offline archives:

Export MASTER images:

.. code-block:: bash

    sudo python3 osir-launcher.py airgap export master

Export AGENT images:

.. code-block:: bash

    sudo python3 osir-launcher.py airgap export agent

Export both components at once:

.. code-block:: bash

    sudo python3 osir-launcher.py airgap export all

.. note::
   Archives are created in:

   ``OSIR/setup/offline_release/``

   Expected files:

   - ``master_containers.tar``
   - ``agent_containers.tar``


Optional components
-------------------

If your deployment uses **Splunk** or **Windows in Docker (Dockur)**,
ensure the corresponding images exist on the export host before running
the airgap export.

These images will automatically be included if they are present locally.


Step 3 — Transfer offline release
---------------------------------

Copy the following directory to the air-gapped host,
keeping the **same OSIR path**:

.. code-block:: text

    OSIR/setup/offline_release/

Optional — Windows in Docker:

If Dockur is used, also copy:

.. code-block:: text

    OSIR/setup/windows_setup/src/dockur_storage/


Step 4 — Load images on the air-gapped host
-------------------------------------------

On the offline machine:

.. code-block:: bash

    cd OSIR

Load MASTER images:

.. code-block:: bash

    sudo python3 osir-launcher.py airgap load master

Load AGENT images:

.. code-block:: bash

    sudo python3 osir-launcher.py airgap load agent

Or load everything:

.. code-block:: bash

    sudo python3 osir-launcher.py airgap load all


Step 5 — Start OSIR in offline mode
-----------------------------------

Start both components:

.. code-block:: bash

    sudo python3 osir-launcher.py start all --offline

This will start MASTER and AGENT without attempting to download images.


Verification
------------

You can verify the installation with:

.. code-block:: bash

    python3 osir-launcher.py status

The launcher will display:

- Process status (MASTER / AGENT)
- Dockerfile fingerprint check (best-effort)

.. note::
   In air-gapped environments the fingerprint status may show:

   - ``OK ✅`` → images match local Dockerfiles
   - ``OUTDATED ⚠️`` → rebuild recommended
   - ``UNKNOWN ❓`` → images were built without fingerprint labels
     or Dockerfile detection was not possible (expected in some offline setups)