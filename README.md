# il2-kills
Identify IL-2 Sturmovik replays with kills in a specific server

## Overview

IL-2 has a very peculiar way of creating replay tracks, much so that content creators may have to go through dozens of tracks to find the ones with interesting kills.

Il2-kills is a script that syncs the in-game tracks with IL2-stats enabled servers to help narrow down the tracks with air and ground kills.

## Installation

### EXE

Il2-kills is released as a Windows executable so no installation or configuration is necessary. Just download, extract and run.

### Python Script

To run `il2-kill.py` script directly, you must have:
 - Python (tested with 3.7);
 - Python `requests` package.
 
 ## Usage
 
### Finding your user id and name

In your web browser, open the server page and navigate to your `sorties` page. The URL should be formatted like one the following (depending on your choice of language):

```
SERVER_ADDRESS/sorties/USER_ID/USER_NAME/?tour=10
SERVER_ADDRESS/en/sorties/USER_ID/USER_NAME/?tour=10
SERVER_ADDRESS/es/sorties/USER_ID/USER_NAME/?tour=10
SERVER_ADDRESS/fr/sorties/USER_ID/USER_NAME/?tour=10
SERVER_ADDRESS/de/sorties/USER_ID/USER_NAME/?tour=10
SERVER_ADDRESS/ru/sorties/USER_ID/USER_NAME/?tour=10
```

Keep the `USER_ID/USER_NAME` **with the forward slash in the middle**.

**Q: Can i get the user id and name from the user profile page?**

A: I wouldn't recommend it because I've seen this number change between the profile page and the sorties page.

### Basic usage

The most basic usage is listing the tracks that contain any air or ground kills.

First open a command prompt (`cmd`), then navigate to the `il2-kills.exe` folder, then enter the following command:

```
il2-kills.exe TRACKS_DIRECTORY MIN_AIR_KILLS MIN_GROUND_KILLS SERVER_ADDRESS USER_ID/USER_NAME
```

Where `TRACKS_DIRECTORY` is the game directory with the `.trk` files, `MIN_AIR_KILLS` is the minimum air kills you want (for instance 1) and `MIN_GROUND_KILLS` is the minimum ground kills you want (for instance also 1).

**Important:** `SERVER_ADDRESS` must start either with `http://` or `https://`.

### Ignoring types of kills

If you want to know the tracks with only air kills or only ground kills, you can disable the kill type you do not want by setting its `MINIMUM` to zero. For instance, to list only the tracks with a minimum of 5 air kills, ignoring the ground kills:

```
il2-kills.exe TRACKS_DIRECTORY 5 0 SERVER_ADDRESS USER_ID/USER_NAME
```

### Renaming tracks

It is possible to rename tracks so you don't have to run the program again for those tracks. To do that just add the `-r` option to the command line like so:

```
il2-kills.exe TRACKS_DIRECTORY MIN_AIR_KILLS MIN_GROUND_KILLS SERVER_ADDRESS USER_ID/USER_NAME -r
```

You will get an indication that renaming is `ON` when the program starts.

**Important:** il2-kills will not work on renamed tracks or copied files because it relies on the creation and modification times. It will do its best to detect modifications and **will not operate on those files**.

### Output to file

Feature comming soon!

### Multiple servers

Feature comming soon!

### Creating a shortcut

You can create a Windows shortcut to make things easier. I recommend doing this with the rename option turned on, because otherwise the program will close after finished and you will not be able to see the output.

To create a shortcut, right-click `il2-kills.exe` and select `Send-to > Desktop (create shortcut)`, right click the shortcut, open `Properties` and add the rest of the command line in the `Target` field:

```
TRACKS_DIRECTORY MIN_AIR_KILLS MIN_GROUND_KILLS SERVER_ADDRESS USER_ID/USER_NAME -r
```

**Q: My Windows is in another language and I can't find the things you described.**

A: Google how to add arguments to your shortcut. There are many tutorials with images.
