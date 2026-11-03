mft
===

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``eztools:filesystem:ntfs:info`` | name_rex: ``r"\$MFT.*\.csv$"``
   * ``eztools:filesystem:ntfs:usn`` | name_rex: ``r"\$J.*.csv$"``

Description
-----------

Parsing of $MFT artifact.

Timeline
--------

**``windows/zimmerman/mft.yml``**

No timeline messages.

**``windows/zimmerman/usn.yml``**

No timeline messages.

Relationships
-------------

**``windows/zimmerman/mft.yml``**

No relationships.

**``windows/zimmerman/usn.yml``**

No relationships.

Fields
------

**``windows/zimmerman/mft.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``custom``
     - 
   * - ``custom``
     - 

**``windows/zimmerman/usn.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``custom``
     - 
   * - ``custom``
     - 
