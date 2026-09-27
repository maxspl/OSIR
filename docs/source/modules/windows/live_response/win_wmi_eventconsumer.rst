win_wmi_eventconsumer
=====================

.. tip:: Ingestion into Splunk.

   **``windows:live_response:wmi_consummer``**

   * name_rex: ``--win_wmi_eventconsumer\.jsonl$``
   * path_suffix: ``win_wmi_eventconsumer``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``WMI``
   * normalize: ``ecs_normalize/windows/live_response/wmi_eventconsumer.vrl``

Description
-----------

Parse EventConsumer.txt from DFIR ORC (powershell.exe Get-WMIObject -Namespace root\\Subscription -Class \_\_EventConsumer command)

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
