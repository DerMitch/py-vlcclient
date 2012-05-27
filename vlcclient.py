# coding: utf-8
"""
    VLCClient
    ~~~~~~~~~

    This module allows to control a VLC instance to be controlled
    via telnet. You need to enable the telnet interface, e.g. start
    VLC like this:

    $ vlc --intf telnet

    More information about the telnet interface:
    http://wiki.videolan.org/Documentation:Streaming_HowTo/VLM

    :author: Michael Mayr <michael@michfrm.net>
    :licence: MIT License
    :version: 0.1.0
"""

"""
ToDo:
- Connection error handling
"""

import sys
import telnetlib

class VLCClient(object):
    """Connection to a running VLC instance."""
    def __init__(self, server, port=4212, password="admin"):
        self.server = server
        self.port = port
        self.password = password

        self.telnet = None

    def connect(self):
        """Connect to VLC and login"""
        assert self.telnet is None, "connect() called twice"
        self.telnet = telnetlib.Telnet()
        self.telnet.open(self.server, self.port)

        # Login
        self.telnet.read_until("Password: ")
        self.telnet.write(self.password)
        self.telnet.write("\n")

        # Password correct?
        result = self.telnet.expect([
            "Password: ",
            ">"
        ])
        if "Password" in result[2]:
            raise WrongPasswordError()

    def disconnect(self):
        """Disconnect and close connection"""
        self.telnet.close()
        self.telnet = None

    def send_command(self, line):
        """Sends a command to VLC and returns the text reply.
        This command may block."""
        self.telnet.write(line + "\n")
        return self.telnet.read_until(">")[1:-3]

    #
    # Commands
    #
    def help(self):
        """Returns the full command reference"""
        return self.send_command("help")

    def status(self):
        """current playlist status"""
        return self.send_command("status")

    def info(self):
        """information about the current stream"""
        return self.send_command("info")

    #
    # Playlist
    #
    def add(self, filename):
        """Add a file to the playlist and play it.
        This command always succeeds."""
        return self.send_command("add {0}".format(filename))

    def enqueue(self, filename):
        """Add a file to the playlist. This command always succeeds."""
        return self.send_command("enqueue {0}".format(filename))

    def seek(self, second):
        """Jump to a position at the current stream if supported."""
        return self.send_command("seek {0}".format(second))

    def play(self):
        """Start/Continue the current stream"""
        return self.send_command("play")

    def pause(self):
        """Pause playing"""
        return self.send_command("pause")

    def stop(self):
        """Stop stream"""
        return self.send_command("stop")

    def rewind(self):
        """Rewind stream"""
        return self.send_command("rewind")

    def next(self):
        """Play next item in playlist"""
        return self.send_command("next")

    def prev(self):
        """Play previous item in playlist"""
        return self.send_command("prev")

    def clear(self):
        """Clear all items in playlist"""
        return self.send_command("clear")

    #
    # Volume
    #
    def volume(self, vol=None):
        """Get the current volume or set it"""
        if vol:
            return self.send_command("volume {0}".format(vol))
        else:
            return self.send_command("volume").strip()

    def volup(self, steps=1):
        """Increase the volume"""
        return self.send_command("volup {0}".format(steps))

    def voldown(self, steps=1):
        """Decrease the volume"""
        return self.send_command("voldown {0}".format(steps))

class WrongPasswordError(Exception):
    pass

def main():
    vlc = VLCClient("::1")
    vlc.connect()

    try:
        command = getattr(vlc, sys.argv[1])
    except IndexError:
        print "usage: vlcclient.py command [argument]"
        sys.exit(1)

    attr = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        print command(attr)
    except TypeError:
        print command()

if __name__ == '__main__':
    main()