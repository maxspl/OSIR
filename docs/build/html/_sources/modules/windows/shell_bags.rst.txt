shell_bags
==========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:registry:hku:shellbags`` | name_rex: ``\.csv$``

Description
-----------

Parsing of shell bags artifact.

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
   * - ``"windows.shellbags"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[file]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Windows ShellBags (registry)"``
     - ``event.provider``
   * - ``"shell_bag"``
     - ``event.code``
   * - ``"shell_bag"``
     - ``event.action``
   * - ``custom``
     - 
   * - ``to_string!(del(.AbsolutePath))``
     - ``file.Ext.shellbags.absolute_path``
   * - ``custom``
     - 
