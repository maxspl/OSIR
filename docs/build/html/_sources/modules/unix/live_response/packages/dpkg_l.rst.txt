dpkg_l
======

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``linux:live_response:packages:dpkg`` | name_rex: ``r"dpkg.*\.jsonl$"``

Description
-----------

Kelly Brazil - JsonConverter - Parsing the output of the command dpkg -l

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
   * - ``to_string!(.name)``
     - ``package.name``
   * - ``to_string!(.version)``
     - ``package.version``
   * - ``to_string!(.architecture)``
     - ``package.architecture``
   * - ``to_string!(.description)``
     - ``package.description``
   * - ``to_string!(.desired)``
     - ``package.install_scope``
   * - ``"dpkg"``
     - ``package.type``
   * - ``to_string!(.status)``
     - ``labels.package_status``
   * - ``to_string!(.codes)``
     - ``labels.package_codes``
   * - ``custom``
     - 
