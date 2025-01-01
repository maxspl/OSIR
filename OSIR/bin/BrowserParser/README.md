## About

Browserparser aims to make parsing of browser data alot easier.
The tool is designed for use with Kape, but can be used manually.
It finds the directories of all browsers on the system, based on the normal locations as of October 2024.
Supports output in JSON or CSV.


## Compatability

Browserparser should be compatible on Linux and Windows. 
The Python script contains functionality to parse push notifications. The compiled binary for Windows does *not* support this, because LevelDB has trouble on Windows.

## Usage

The tool can be used on the disk directly, using the drive letter as the source directory.

```python3 main.py <sourcedir> <outputdir> --csv / --json```


## Output

The tool parses the following artifacts on these browsers:

* Chromium
    * Chrome
       * Downloads
       * Browsing-history
       * Visited links
       * Searched
       * Favicons
       * Cookies
       * Shortcuts
       * Notifications (Only in the python script!)
       * Extensions
    * Edge
       * Downloads
       * Browsing-history
       * Visited links
       * Searched
       * Favicons
       * Cookies
       * Shortcuts
       * Notifications (Only in the python script!)
       * Extensions
    * Opera
       * Downloads
       * Browsing-history
       * Visited links
       * Searched
       * Favicons
       * Cookies
       * Shortcuts
       * Notifications (Only in the python script!)
       * Extensions
    * Yandex
       * Downloads
       * Browsing-history
       * Visited links
       * Searched
       * Favicons
       * Cookies
       * Shortcuts
       * Notifications (Only in the python script!)
       * Extensions
    * Brave
       * Downloads
       * Browsing-history
       * Visited links
       * Searched
       * Favicons
       * Cookies
       * Shortcuts
       * Notifications (Only in the python script!)
       * Extensions
* Non-Chromium
    * Firefox
       * Cookies
       * Form-history
       * Permissions
       * Bookmarks
       * Browsing-history
         * "Regular" history
         * "Enriched" history (History with extra metadata)
       * Extensions
       * Logins
       * Downloads
       * Favicons
       * Notifications

