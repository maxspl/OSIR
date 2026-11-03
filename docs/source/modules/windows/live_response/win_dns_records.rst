win_dns_records
===============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:dns_records`` | name_rex: ``r"--dns_records\.jsonl$"``

Description
-----------

Parse DNS\_records.txt from DFIR ORC (custom ps1 command)

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
   * - ``"Windows enumlocs volume inventory"``
     - ``event.provider``
   * - ``custom``
     - 
   * - ``to_string!(del(.volume_id))``
     - ``action.properties.volume_id``
   * - ``to_string!(del(.filesystem))``
     - ``action.properties.volume_filesystem``
   * - ``to_string!(del(.status))``
     - ``action.properties.volume_status``
   * - ``del(.entries)``
     - ``action.properties.volume_entries``
   * - ``del(.MountedVolume)``
     - ``action.properties.volume_mounted_volumes``
   * - ``del(.PhysicalDriveVolume)``
     - ``action.properties.volume_physical_drive_volume_raw``
   * - ``del(.DiskInterfaceVolume)``
     - ``action.properties.volume_disk_interface_volume_raw``
   * - ``del(.Snapshot)``
     - ``action.properties.volume_snapshots``
   * - ``custom``
     - 
