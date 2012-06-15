py-vlcclient
============

This module allows to control a VLC instance using Python. This
module uses the telnet interface of VLC and has no external dependencies.

More information about the telnet interface:
http://wiki.videolan.org/Documentation:Streaming_HowTo/VLM

The clients supports some basic commands to modify playlists and control the playback.

How to Use
==========

First start VLC and enable the telnet interface. You can either enable
it when starting VLC::

   $ vlc --intf telnet

or with network access:

    $ vlc --intf telnet --lua-config "telnet={host='0.0.0.0:4212'}"

or via the menus (depending on your platform, mostly View ->
Add Interface -> Telnet).

Example usage::

  >>> from vlcclient import VLCClient
  >>> vlc = VLCClient("::1")
  >>> vlc.connect()
  >>>
  >>> r.add("/home/mitch/Music/a_song.ogg")
  >>> r.volume(300)
  >>> r.rewind()
  >>> r.status()
  '( new input: file:///.... )
   ( audio volume: 200 )
   ( state playing )'


Implemented Commands
====================

The following commands are currently implemented:

generic
-------

 * help
 * status
 * info

playlists and controls
----------------------

 * add
 * enqueue
 * seek
 * play
 * pause
 * stop
 * rewind
 * next
 * prev
 * clear

volume
------

 * volume (get/set)
 * volup
 * voldown
