win_dns_cache
=============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:dns_cache`` | name_rex: ``r"--win_dns_cache\.jsonl$"``

Description
-----------

Parse dns\_cache.txt from DFIR ORC (ipconfig.exe /displaydns command). Output fields lang depends on the system lang

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
   * - ``custom``
     - 
   * - ``"Windows DNS Cache"``
     - ``event.provider``
   * - ``"answer"``
     - ``dns.type``
   * - ``"dns"``
     - ``network.protocol``
   * - ``custom``
     - 
