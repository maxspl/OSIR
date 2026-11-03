win_tcpvcon
===========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:sysinternals:tcpvcon`` | name_rex: ``r"--win_tcpvcon\.jsonl$"``

Description
-----------

Parse routes.txt from DFIR ORC (Tcpvcon.exe -a -n -c command)

Timeline
--------

No timeline messages.

Relationships
-------------

No relationships.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Sysinternals Tcpvcon"``
     - ``event.provider``
   * - ``"ip"``
     - ``network.protocol``
   * - ``type``
     - ``action.properties.type``
   * - ``downcase(protocol)``
     - ``network.transport``
   * - ``downcase(protocol)``
     - ``network.protocol``
   * - ``process_name``
     - ``process.name``
   * - ``to_int(pid)``
     - ``process.pid``
   * - ``state``
     - ``action.properties.tcp_state``
   * - ``"ingress"``
     - ``network.direction``
   * - ``local_address``
     - ``source.ip``
   * - ``remote_address``
     - ``destination.ip``
   * - ``"ipv4"``
     - ``network.type``
   * - ``"ipv6"``
     - ``network.type``
