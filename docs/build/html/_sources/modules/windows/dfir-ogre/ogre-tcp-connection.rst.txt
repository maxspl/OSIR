ogre-tcp-connection
===================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:sysinternals:tcpvcon`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of tcpvcon - using ANSSI DFIR OGRE

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
   * - ``local_adress``
     - ``source.ip``
   * - ``remote_adress``
     - ``destination.ip``
   * - ``"ipv4"``
     - ``network.type``
   * - ``"ipv6"``
     - ``network.type``
