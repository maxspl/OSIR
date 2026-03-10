.. _api_usage:

============================
API & Client Usage
============================

This document provides comprehensive information about the OSIR API endpoints
and how to use them through the OSIR client.

.. contents:: Table of Contents
   :depth: 2
   :local:
   :backlinks: none

----

API Base URL
============

The OSIR API is typically available at ``http://localhost:8502`` with the following base paths:

- ``/`` — Home page with API documentation links
- ``/api`` — API endpoints prefix
- ``/docs`` — Interactive API documentation (Swagger UI)

You can review all available actions through the API using the ``/docs`` endpoint.

Authentication
==============

.. warning::

   The OSIR API currently does not require authentication.

----

OsirClient Class Reference
==========================

The ``OsirClient`` class is the main entry point for interacting with the OSIR API.

Initialization
--------------

.. code-block:: python

    from osir_client.client.OsirClient import OsirClient

    client = OsirClient(api_url="http://localhost:8502")

    if client.is_active():
        print("API is running")

    client._check_version()

----

Command-Line Interface
======================

The OSIR client provides a comprehensive CLI for interacting with the API.

Basic Syntax
------------

.. code-block:: bash

    OsirClient.py [GLOBAL_OPTIONS] COMMAND ACTION [ACTION_OPTIONS]

**Global Options:**

- ``-u, --api-url`` — OSIR API URL (default: ``$OSIR_API_URL`` environment variable)
- ``-h, --help`` — Show help message

Environment Configuration
-------------------------

Create a ``.env`` file to avoid specifying the API URL each time:

.. code-block:: bash

    OSIR_API_URL="http://localhost:8502"

Case Commands
-------------

.. code-block:: bash

    # List all cases
    OsirClient.py case list

    # Create a new case
    OsirClient.py case create -c "my_investigation"

Module Commands
---------------

.. code-block:: bash

    # List all modules
    OsirClient.py module list

    # Filter by category
    OsirClient.py module list-category -cat windows
    OsirClient.py module list-category -cat windows -sub live_response
    OsirClient.py module list-category -cat windows -sub live_response -subsub process

    # Check if a module exists
    OsirClient.py module exists -m "bodyfile.yml"

    # Run a module
    OsirClient.py module run -c "test_case" -m "dummy.yml"

    # Run and wait for completion
    OsirClient.py module run -c "test_case" -m "dummy.yml" -w

    # Run with an input file
    OsirClient.py module run -c "test_case" -m "dummy.yml" -i "input_dummy.raw"

Profile Commands
----------------

.. code-block:: bash

    # List all profiles
    OsirClient.py profile list

    # Check if a profile exists
    OsirClient.py profile exists -p "uac.yml"

    # Run a profile
    OsirClient.py profile run -c "test_case" -p "uac.yml"

    # Run and wait for completion
    OsirClient.py profile run -c "test_case" -p "uac.yml" -w

Handler Commands
----------------

.. code-block:: bash

    # List handlers for a case
    OsirClient.py handler list -c "test_case"

    # Get handler status
    OsirClient.py handler status -i "handler-uuid-here"

    # Get status and wait for completion
    OsirClient.py handler status -i "handler-uuid-here" -w

Task Commands
-------------

.. code-block:: bash

    # List tasks for a case
    OsirClient.py task list -c "test_case"

    # Get task information
    OsirClient.py task info -i "task-uuid-here"

----

Complete Workflow Examples
==========================

Basic Investigation
-------------------

.. code-block:: python

    from osir_client.client.OsirClient import OsirClient

    client = OsirClient(api_url="http://localhost:8502")

    if not client.is_active():
        raise SystemExit("OSIR API is not running")

    case = client.cases.create("investigation_2024")
    case.modules.list(print=True)

    handler = case.modules.run("mactime")
    if handler and handler.handler_id:
        task_ids = handler._get_handler_task_ids(handler.handler_id)
        for task_id in task_ids:
            task_info = case.tasks.get_task_info(task_id)
            print(f"Task {task_id}: {task_info.status}")

Profile Execution
-----------------

.. code-block:: python

    from osir_client.client.OsirClient import OsirClient

    client = OsirClient(api_url="http://localhost:8502")

    if not client.is_active():
        raise SystemExit("OSIR API is not running")

    case = client.cases.create("profile_execution")

    handler = case.profiles.run("uac")
    if handler and handler.handler_id:
        task_ids = handler._get_handler_task_ids(handler.handler_id)
        for i, task_id in enumerate(task_ids, 1):
            task_info = case.tasks.get_task_info(task_id, print=False)
            print(f"  {i}. Task {task_id}: {task_info.status} ({task_info.task_type})")

CLI Workflows
-------------

**Basic investigation:**

.. code-block:: bash

    OsirClient.py case create -c "investigation_2024"
    OsirClient.py module list
    OsirClient.py module run -c "investigation_2024" -m "mactime.yml" -w
    OsirClient.py task list -c "investigation_2024"

**Profile execution:**

.. code-block:: bash

    OsirClient.py case create -c "orc_invest"
    OsirClient.py profile list
    OsirClient.py profile run -c "orc" -p "DFIR_ORC.yml" -w

----

Advanced Usage
==============

Batch Operations
----------------

.. code-block:: python

    modules_to_run = ["mactime", "audit", "journal"]

    for module_name in modules_to_run:
        handler = case.modules.run(module_name)
        status = handler.handler_id if handler and handler.handler_id else "failed"
        print(f"{module_name}: {status}")

Multiple Cases
--------------

.. code-block:: python

    case1 = client.cases.create("investigation_a")
    case2 = client.cases.create("investigation_b")

    handler1 = case1.modules.run("mactime.yml")
    handler2 = case2.modules.run("dummy.yml",
                                 input_path="/path/to/file.exe")