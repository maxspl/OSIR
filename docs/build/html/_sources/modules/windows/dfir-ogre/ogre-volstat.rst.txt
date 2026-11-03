ogre-volstat
============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:filesystem:volume:info`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of volstats - using ANSSI DFIR OGRE

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
   * - ``"Windows volume statistics (FatInfo volstats)"``
     - ``event.provider``
   * - ``computer_name``
     - ``host.name``
   * - ``volumeid``
     - ``action.properties.volumeid``
   * - ``location``
     - ``action.properties.location``
   * - ``volume_type``
     - ``action.properties.volume_type``
   * - ``is_parsed``
     - ``action.properties.is_parsed``
   * - ``mount_point``
     - ``action.properties.mount_point``
