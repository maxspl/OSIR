Install OSIR
============

This page describes how to install and start OSIR. For the architecture
overview and the prerequisites of each use case (all in one, Windows host,
distributed), see :doc:`basics/getting_started`.

Requirements
------------

- A Linux or Windows (via WSL 2) host
- `Docker <https://docs.docker.com/get-docker/>`_ and Docker Compose
- If you need to run Windows tools: a Windows box (VM deployed automatically
  via Vagrant/Dockur, or an existing VM with an admin account and WinRM enabled)

Get the code
------------

Clone the repository with its submodules:

.. code-block:: bash

    git clone --recurse-submodules https://github.com/maxspl/OSIR.git

Install and start
------------------

OSIR is installed and started with the unified launcher ``osir-launcher.py``:

.. code-block:: bash

    cd OSIR
    python3 osir-launcher.py start all

This command installs and starts both the MASTER and AGENT components.

.. warning::
   The first execution can take time because Docker images, dependencies and,
   if needed, the Windows VM of the agent may be downloaded.

Components can also be installed separately:

.. code-block:: bash

    python3 osir-launcher.py start master
    python3 osir-launcher.py start agent

Check the status
----------------

.. code-block:: bash

    python3 osir-launcher.py status

The command displays an overview table and checks, for each component, that the
Docker container is running and that the expected OSIR process runs inside it.

Stop OSIR
---------

.. code-block:: bash

    python3 osir-launcher.py stop master
    python3 osir-launcher.py stop agent
    python3 osir-launcher.py stop all

Optional flags (``--images``, ``--vagrant``, ``--dockur``) also remove the
related Docker images or stop the Windows VM.

Going further
-------------

- :doc:`setup/master_setup` — detailed MASTER setup and configuration files
- :doc:`setup/agent_setup` — detailed AGENT setup and configuration files
- :doc:`setup/developer_mode` — developer mode for module development
- :doc:`setup/air_gap_setup` — air-gapped installation
- :doc:`basics/getting_started` — network requirements and first steps with a case
