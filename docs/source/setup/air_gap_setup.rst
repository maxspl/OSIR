Air Gap Setup
==============

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
    python3 osir-launcher.py start all

This ensures all required images are built locally.

Step 2 — Export Docker images
------------------------------

Use the launcher to generate offline archives:

Export MASTER images:

.. code-block:: bash

    python3 osir-launcher.py airgap export master

Export AGENT images:

.. code-block:: bash

    python3 osir-launcher.py airgap export agent

Export both components at once:

.. code-block:: bash

    python3 osir-launcher.py airgap export all

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

    python3 osir-launcher.py airgap load master

Load AGENT images:

.. code-block:: bash

    python3 osir-launcher.py airgap load agent

Or load everything:

.. code-block:: bash

    python3 osir-launcher.py airgap load all

Step 5 — Start OSIR in offline mode
-----------------------------------

Start both components:

.. code-block:: bash

    python3 osir-launcher.py start all --offline

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
