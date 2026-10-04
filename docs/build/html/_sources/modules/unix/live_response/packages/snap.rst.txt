snap
====

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``linux:live_response:packages:snap`` | name_rex: ``r"snap.*\.jsonl$"``

Description
-----------

Kelly Brazil - JsonConverter - Parsing the output of the command snap

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
   * - ``name``
     - ``package.name``
   * - ``version``
     - ``package.version``
   * - ``rev``
     - ``package.reference``
   * - ``tracking``
     - ``package.type``
   * - ``publisher``
     - ``package.vendor``
   * - ``Notes``
     - ``message``
