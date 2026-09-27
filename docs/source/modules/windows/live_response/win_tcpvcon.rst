win_tcpvcon
===========

.. tip:: Ingestion into Splunk.

   **``windows:live_response:win_tcpvcon``**

   * name_rex: ``--win_tcpvcon\.jsonl$``
   * path_suffix: ``win_tcpvcon``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``TCPVCON``
   * normalize: ``ecs_normalize/windows/live_response/tcpvcon.vrl``

Description
-----------

Parse routes.txt from DFIR ORC (Tcpvcon.exe -a -n -c command)

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
