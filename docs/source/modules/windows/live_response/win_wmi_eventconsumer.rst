win_wmi_eventconsumer
=====================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:wmi_consummer`` | name_rex: ``--win_wmi_eventconsumer\.jsonl$``

Description
-----------

Parse EventConsumer.txt from DFIR ORC (powershell.exe Get-WMIObject -Namespace root\\Subscription -Class \_\_EventConsumer command)

Timeline
--------

No timeline messages.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``"windows.wmi_eventconsumer"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[configuration]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"wmi_eventconsumer"``
     - ``event.action``
   * - ``"success"``
     - ``event.outcome``
   * - ``custom``
     - 
   * - ``to_string!(del(.MachineName))``
     - ``wmi.event_consumer.machine_name``
   * - ``to_string!(del(.__SERVER))``
     - ``wmi.event_consumer.server``
   * - ``to_string!(del(.UNCServerName))``
     - ``wmi.event_consumer.unc_server_name``
   * - ``to_string!(del(.__CLASS))``
     - ``wmi.event_consumer.class``
   * - ``to_string!(del(.__SUPERCLASS))``
     - ``wmi.event_consumer.superclass``
   * - ``to_string!(del(.__DYNASTY))``
     - ``wmi.event_consumer.dynasty``
   * - ``to_string!(del(.__DERIVATION))``
     - ``wmi.event_consumer.derivation``
   * - ``custom``
     - 
   * - ``to_string!(del(.__NAMESPACE))``
     - ``wmi.event_consumer.namespace``
   * - ``to_string!(del(.__PATH))``
     - ``wmi.event_consumer.path``
   * - ``to_string!(del(.__RELPATH))``
     - ``wmi.event_consumer.relpath``
   * - ``custom``
     - 
   * - ``to_string!(del(.type))``
     - ``wmi.event_consumer.source_type``
   * - ``custom``
     - 
   * - ``to_string!(del(.DesktopName))``
     - ``wmi.event_consumer.desktop_name``
   * - ``to_string!(del(.WindowTitle))``
     - ``wmi.event_consumer.window_title``
   * - ``custom``
     - 
