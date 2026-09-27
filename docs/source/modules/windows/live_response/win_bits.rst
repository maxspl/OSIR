win_bits
========

.. tip:: Ingestion into Splunk.

   **``windows:live_response:bits``**

   * name_rex: ``--win_bits\.jsonl$``
   * path_suffix: ``win_bits``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``BITS``
   * normalize: ``ecs_normalize/windows/live_response/bits.vrl``

Description
-----------

Parse BITS\_jobs.txt from DFIR ORC (bitsadmin.exe /list /allusers /verbose command)

Timeline
--------

Placeholder table for the messages created for the timeline.

.. list-table::
   :header-rows: 1

   * - Timeline
     - ECS field
     - Message
   * -
     -
     -

Fields
------

Placeholder table for the output fields.

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * -
     -
