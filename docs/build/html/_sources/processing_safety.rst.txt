Processing safety
=================

OSIR monitors case directories and creates processing tasks when files or directories match module inputs.
Some artifacts are produced progressively by previous modules, uploads, archive extraction, or external tools.
To avoid processing incomplete inputs, OSIR applies several safeguards before task execution.

File stability safety
---------------------

For file inputs discovered by the watcher, OSIR does not immediately push a task as soon as a matching path appears.

A file is considered stable when one of the following conditions is true:

- its modification time is older than ``OSIR_FILE_STABILITY_WINDOW``;
- its size and modification time remain unchanged for ``OSIR_FILE_STABILITY_WINDOW``.

Unstable files are kept in a delayed queue and retried by the monitoring loop. Once stable, the task is released and pushed to the task queue.

Default environment variables:

.. code-block:: bash

   OSIR_FILE_STABILITY_WINDOW=1.0

Agent-side stability check
--------------------------

The watcher stability safety covers the normal monitored-path workflow.

For manually pushed tasks or API-created tasks, the agent keeps an additional safety check before processing file inputs. It waits until the file looks stable, using:

.. code-block:: bash

   OSIR_FILE_STABILITY_WINDOW=1.0
   OSIR_FILE_STABILITY_CHECK_INTERVAL=0.2
   OSIR_FILE_STABILITY_MAX_WAIT=300

If the file is still changing after ``OSIR_FILE_STABILITY_MAX_WAIT``, OSIR logs a warning and starts the task anyway to avoid blocking the worker indefinitely.
This fallback mainly protects manual or API-created tasks that may not have gone through the watchdog stability delay.

Directory idle detection
------------------------

For directory inputs, OSIR does not process a directory immediately after it appears.

A timer is started when a matching directory is detected. The directory is processed only when its modification time remains unchanged for the configured cooldown period.

If the directory is still changing, the idle check is rescheduled.

This protects directory-based modules against incomplete extraction or copy operations.

Parent directory protection
---------------------------

Before processing a directory, OSIR checks whether it is the parent of another directory still waiting for idle processing.

If it is a parent of another pending idle directory, OSIR skips the parent execution to avoid processing a broader directory while a more specific child directory is still being stabilized.

Input in-use check
------------------

Before a worker executes a task, OSIR checks whether the same input is already used by another active task in the same case.

If another task is still using the input, the worker waits and retries before executing the module.

This prevents concurrent modules from reading or processing the same input while another module is still operating on it.

``hold_consumers`` barrier
--------------------------

Some producer modules create directories that are consumed by downstream modules.
For these modules, ``hold_consumers`` can be enabled in the module configuration.

Example:

.. code-block:: yaml

   configuration:
     module: extract_orc
     type: pre-process
     disk_only: true
     no_multithread: true
     hold_consumers: true

When ``hold_consumers`` is set to ``true``:

- OSIR tracks the producer module output directory
- matching consumer directory tasks under this output are deferred
- consumers are released only when all producer tasks for the case are finished

This is useful for modules such as archive extraction, where downstream modules must not consume partially extracted folders.

Task batching and delayed flush
-------------------------------

File tasks matched by compiled watcher rules are buffered and pushed in batches.

The batch flush performs:

- bulk database task creation;
- bulk Celery task publication using a reused producer connection.

Before a handler exits, OSIR waits for:

- pending file batches;
- delayed unstable file tasks;
- deferred ``hold_consumers`` directory tasks;
- active directory idle timers;
- active processing tasks.

This prevents the handler from being marked as completed while work is still buffered or delayed.