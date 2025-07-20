# Splunk App for DECODE

This package is a dashboard app for Splunk to exploit results of [DECODE](https://github.com/ANSSI-FR/DECODE) tool.

There is no package requirements to install the app.

## Installation

Copy this current folder `Splunk_App_DECODE` into `$SPLUNK_HOME/etc/apps/`.

## Data ingestion

This app adds a sourcetype `anssi:decode` (described in `props.conf` file) corresponding to DECODE results.  

In order to add data, you can :
- manually add single a file :
```
./splunk add oneshot "/path/to/decode/results/folder/hostname.csv" -sourcetype "anssi:decode" -index ##INDEX_NAME## -host ##HOSTNAME##
```

- monitor a folder (add configuration in the file `inputs.conf`) :

```
[monitor:///path/to/decode/results/folder/]
disabled = false
host_regex = /([^/]+)\.csv
sourcetype = anssi:decode
index = ##INDEX_NAME##
crcSalt = <SOURCE>
```

## Context view

The contextual view of the dashboard allows the user to view the occurrences of a selected file in a timeline. It allows to quickly see what happened on the machine around these events.

This timeline can be selected by the user in the `Timeline sourcetype` drop-down menu.  
Once the timeline is selected, simply click on a file of interest and the "context" view is updated. The file occurrences are colored red for greater visibility.

To generate this timeline you can use the [orc2timeline](https://github.com/ANSSI-FR/orc2timeline) tool developed by ANSSI.