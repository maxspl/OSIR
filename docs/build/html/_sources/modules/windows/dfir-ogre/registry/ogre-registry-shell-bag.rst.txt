ogre-registry-shell-bag
=======================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:ogre:registry_shell_bag`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of shellbags - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-shell_bags-interacted-with:
.. _tl-windows-shell_bags-referenced:

.. list-table::
   :header-rows: 1

   * - labels.has_explored
     - Relation
     - Message
   * - ``True``
     - `interacted-with <rel-windows-shell_bags-interacted-with_>`_
     - ``User {user.name} interacted with {labels.absolute_path}``
   * - ``False``
     - `referenced <rel-windows-shell_bags-referenced_>`_
     - ``Shellbag entry exists for {labels.absolute_path} (no evidence of user interaction)``

Relationships
-------------

.. _rel-windows-shell_bags-interacted-with:
.. _rel-windows-shell_bags-referenced:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `interacted-with <tl-windows-shell_bags-interacted-with_>`_
     - ``user.name``
     - ``labels.value``
     - ``interacted with``
   * - `referenced <tl-windows-shell_bags-referenced_>`_
     - ``user.name``
     - ``labels.value``
     - ``referenced``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``parse_timestamp(LastWriteTime)``
     - ``timestamp``
   * - ``parse_timestamp(FirstInteracted)``
     - ``timestamp``
   * - ``parse_timestamp(LastInteracted)``
     - ``timestamp``
   * - ``BagPath``
     - ``labels.bag_path``
   * - ``AbsolutePath``
     - ``labels.absolute_path``
   * - ``ShellType``
     - ``labels.shell_type``
   * - ``Value``
     - ``labels.value``
   * - ``Miscellaneous``
     - ``labels.misc``
   * - ``Value``
     - ``file.name``
   * - ``Value``
     - ``file.directory``
   * - ``to_int(Slot)``
     - ``labels.slot``
   * - ``to_int(NodeSlot)``
     - ``labels.node_slot``
   * - ``to_int(MRUPosition)``
     - ``labels.mru_position``
   * - ``to_int(ChildBags)``
     - ``labels.child_bags``
   * - ``to_int(MFTSequenceNumber)``
     - ``labels.mft_sequence``
   * - ``to_int(ExtensionBlockCount)``
     - ``labels.extension_block_count``
   * - ``to_bool(HasExplored)``
     - ``labels.has_explored``
   * - ``parse_timestamp(LastWriteTime)``
     - ``labels.last_write_time``
   * - ``parse_timestamp(FirstInteracted)``
     - ``labels.first_interacted``
   * - ``parse_timestamp(LastInteracted)``
     - ``labels.last_interacted``
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
   * - ``name``
     - ``labels.value``
   * - ``type``
     - ``labels.shell_type``
   * - ``localized_name``
     - ``labels.localized_name``
   * - ``description``
     - ``labels.description``
   * - ``key_security``
     - ``labels.key_security``
   * - ``ogre_md``
     - ``labels.ogre_md``
   * - ``file_reference``
     - ``file.inode``
   * - ``replace(to_string!(.path), pattern: "\\\\", with: "\\")``
     - ``labels.absolute_path``
   * - ``parse_timestamp(key_modif_time)``
     - ``timestamp``
   * - ``parse_timestamp(key_modif_time)``
     - ``registry.mtime``
   * - ``parse_timestamp(modification_time)``
     - ``file.mtime``
   * - ``parse_timestamp(access_time)``
     - ``file.accessed``
   * - ``parse_timestamp(creation_time)``
     - ``file.created``
   * - ``replace(to_string!(.key_path), pattern: "\\\\", with: "\\")``
     - ``registry.path``
   * - ``true``
     - ``labels.has_explored``
