win_netstat
===========

.. tip:: Ingestion into Splunk.

   **``windows:live_response:netstat``**

   * name_rex: ``--win_netstat\.jsonl$``
   * path_suffix: ``win_netstat``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``NETSTAT``
   * normalize: ``ecs_normalize/windows/live_response/netstat.vrl``

Description
-----------

Parse netstat.txt from DFIR ORC (netstat.exe -a -n -o command)

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
