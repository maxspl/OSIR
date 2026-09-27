mft
===

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``filesystem:ntfs:info`` | name_rex: ``\$MFT.*\.csv$``
   * ``filesystem:ntfs:usn`` | name_rex: ``\$J.*.csv$``

Description
-----------

Parsing of $MFT artifact.

Timeline
--------

**``windows/mft.yml``**

No timeline messages.

**``windows/usn.yml``**

No timeline messages.

Fields
------

**``windows/mft.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``custom``
     - 
   * - ``"event"``
     - ``event.kind``
   * - ``[file]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"mft"``
     - ``event.module``
   * - ``custom``
     - 

**``windows/usn.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``custom``
     - 
   * - ``"event"``
     - ``event.kind``
   * - ``[file]``
     - ``event.category``
   * - ``[change]``
     - ``event.type``
   * - ``"usn"``
     - ``event.module``
   * - ``custom``
     - 
