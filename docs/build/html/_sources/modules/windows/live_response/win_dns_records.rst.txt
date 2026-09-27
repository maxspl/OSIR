win_dns_records
===============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:dns_records`` | name_rex: ``--dns_records\.jsonl$``

Description
-----------

Parse DNS\_records.txt from DFIR ORC (custom ps1 command)

Timeline
--------

No timeline messages.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``custom``
     - 
   * - ``"windows.enumlocs"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[host, configuration]``
     - ``event.category``
   * - ``[info, inventory]``
     - ``event.type``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Windows enumlocs volume inventory"``
     - ``event.provider``
   * - ``custom``
     - 
   * - ``to_string!(del(.volume_id))``
     - ``host.Ext.enumlocs.volume.id``
   * - ``to_string!(del(.filesystem))``
     - ``host.Ext.enumlocs.volume.filesystem``
   * - ``to_string!(del(.status))``
     - ``host.Ext.enumlocs.volume.status``
   * - ``del(.entries)``
     - ``host.Ext.enumlocs.volume.entries``
   * - ``del(.MountedVolume)``
     - ``host.Ext.enumlocs.volume.mounted_volumes``
   * - ``del(.PhysicalDriveVolume)``
     - ``host.Ext.enumlocs.volume.physical_drive_volume_raw``
   * - ``del(.DiskInterfaceVolume)``
     - ``host.Ext.enumlocs.volume.disk_interface_volume_raw``
   * - ``del(.Snapshot)``
     - ``host.Ext.enumlocs.volume.snapshots``
   * - ``custom``
     - 
