shell_bags
==========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``eztools:windows:registry:shell_bags`` | name_rex: ``r"\.csv$"``

Description
-----------

Parsing of shell bags artifact.

Timeline
--------

.. _tl-windows-zimmerman-shell_bags-interacted-with:
.. _tl-windows-zimmerman-shell_bags-referenced:

.. list-table::
   :header-rows: 1

   * - action.properties.HasExplored
     - Relation
     - Message
   * - ``True``
     - `interacted-with <rel-windows-zimmerman-shell_bags-interacted-with_>`_
     - ``User {user.name} interacted with {action.properties.AbsolutePath}``
   * - ``False``
     - `referenced <rel-windows-zimmerman-shell_bags-referenced_>`_
     - ``Shellbag entry exists for {action.properties.AbsolutePath} (no evidence of user interaction)``

Relationships
-------------

.. _rel-windows-zimmerman-shell_bags-interacted-with:
.. _rel-windows-zimmerman-shell_bags-referenced:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `interacted-with <tl-windows-zimmerman-shell_bags-interacted-with_>`_
     - ``user.name``
     - ``action.properties.value``
     - ``interacted with``
   * - `referenced <tl-windows-zimmerman-shell_bags-referenced_>`_
     - ``user.name``
     - ``action.properties.value``
     - ``referenced``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``parse_timestamp(LastWriteTime)``
     - ``timestamp``
   * - ``parse_timestamp(FirstInteracted)``
     - ``timestamp``
   * - ``parse_timestamp(LastInteracted)``
     - ``timestamp``
   * - ``BagPath``
     - ``action.properties.BagPath``
   * - ``AbsolutePath``
     - ``action.properties.AbsolutePath``
   * - ``ShellType``
     - ``action.properties.shell_type``
   * - ``Value``
     - ``action.properties.value``
   * - ``Miscellaneous``
     - ``action.properties.Miscellaneous``
   * - ``Value``
     - ``file.name``
   * - ``Value``
     - ``file.directory``
   * - ``to_int(Slot)``
     - ``action.properties.Slot``
   * - ``to_int(NodeSlot)``
     - ``action.properties.NodeSlot``
   * - ``to_int(MRUPosition)``
     - ``action.properties.MRUPosition``
   * - ``to_int(ChildBags)``
     - ``action.properties.ChildBags``
   * - ``to_int(MFTSequenceNumber)``
     - ``action.properties.MFTSequenceNumber``
   * - ``to_int(ExtensionBlockCount)``
     - ``action.properties.ExtensionBlockCount``
   * - ``to_bool(HasExplored)``
     - ``action.properties.HasExplored``
   * - ``parse_timestamp(LastWriteTime)``
     - ``action.properties.LastWriteTime``
   * - ``parse_timestamp(FirstInteracted)``
     - ``action.properties.FirstInteracted``
   * - ``parse_timestamp(LastInteracted)``
     - ``action.properties.LastInteracted``
   * - ``parse_timestamp(CreatedOn)``
     - ``file.created``
   * - ``parse_timestamp(ModifiedOn)``
     - ``file.mtime``
   * - ``parse_timestamp(AccessedOn)``
     - ``file.accessed``
   * - ``to_int(MFTEntry)``
     - ``file.inode``
   * - ``"HKCU"``
     - ``registry.hive``
   * - ``parse_timestamp(LastWriteTime)``
     - ``registry.mtime``
   * - ``"HKCU\\Local Settings\\Software\\Microsoft\\Windows\\Shell\\" + replace(to_string!(.BagPath), pattern: "\\\\", with: "\\")``
     - ``registry.path``
