Developer Mode
==============

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
--------------------

It is recommended to use **two terminals**.

Terminal 1: MASTER
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Start MASTER in developer mode:

.. code-block:: bash

    python3 osir-launcher.py start master --attach --debug-shell

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Start AGENT in developer mode:

.. code-block:: bash

    python3 osir-launcher.py start agent --attach --debug-shell

Inside the container shell, launch:

.. code-block:: bash

    OSIR.py --agent

You will now see AGENT logs live in this terminal.
This allows you to:

- Observe processing logs live
- Restart the agent process quickly
- Test modules without rebuilding containers

Why use developer mode?
-----------------------

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

