# coding: utf-8
"""
    VLCClient
    ~~~~~~~~~

    This module allows to control a VLC instance through a python interface.
    
    You need to enable the telnet interface, e.g. start
    VLC like this:

    $ vlc --intf telnet

    To start VLC with allowed remote admin:
    $ vlc --intf telnet --lua-config "telnet={host='0.0.0.0:4212'}"
    
    Replace --intf with --extraintf to start telnet and the regular GUI

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
    def __init__(self, server, port=4212, password="admin", timeout=5):
        self.server = server
        self.port = port
        self.password = password
        self.timeout = timeout

        self.telnet = None
        self.server_version = None

    def connect(self):
        """Connect to VLC and login"""
        assert self.telnet is None, "connect() called twice"
        self.telnet = telnetlib.Telnet()
        self.telnet.open(self.server, self.port, self.timeout)

        # Parse version
        result = self.telnet.expect([
            "VLC media player ([\d.]+)",
        ])
        self.server_version = result[1].group(1)
        self.server_version_tuple = self.server_version.split('.')

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

    def _send_command(self, line):
        """Sends a command to VLC and returns the text reply.
        This command may block."""
        self.telnet.write(line + "\n")
        return self.telnet.read_until(">")[1:-3]

    def _require_version(self, command, version):
        if isinstance(version, basestring):
            version = version.split('.')
        if version > self.server_version_tuple:
            raise OldServerVersion("Command '{0} requires at least VLC {1}".format(
                command, ".".join(version)
            ))

    #
    # Commands
    #
    def help(self):
        """Returns the full command reference"""
        return self._send_command("help")

    def status(self):
        """current playlist status"""
        self._require_version("status", "2.0.0")
        return self._send_command("status")

    def info(self):
        """information about the current stream"""
        return self._send_command("info")

    #
    # Playlist
    #
    def add(self, filename):
        """Add a file to the playlist and play it.
        This command always succeeds."""
        return self._send_command("add {0}".format(filename))

    def enqueue(self, filename):
        """Add a file to the playlist. This command always succeeds."""
        return self._send_command("enqueue {0}".format(filename))

    def seek(self, second):
        """Jump to a position at the current stream if supported."""
        return self._send_command("seek {0}".format(second))

    def play(self):
        """Start/Continue the current stream"""
        return self._send_command("play")

    def pause(self):
        """Pause playing"""
        return self._send_command("pause")

    def stop(self):
        """Stop stream"""
        return self._send_command("stop")

    def rewind(self):
        """Rewind stream"""
        return self._send_command("rewind")

    def next(self):
        """Play next item in playlist"""
        return self._send_command("next")

    def prev(self):
        """Play previous item in playlist"""
        return self._send_command("prev")

    def clear(self):
        """Clear all items in playlist"""
        return self._send_command("clear")

    #
    # Volume
    #
    def volume(self, vol=None):
        """Get the current volume or set it"""
        if vol:
            return self._send_command("volume {0}".format(vol))
        else:
            return self._send_command("volume").strip()

    def volup(self, steps=1):
        """Increase the volume"""
        return self._send_command("volup {0}".format(steps))

    def voldown(self, steps=1):
        """Decrease the volume"""
        return self._send_command("voldown {0}".format(steps))

class WrongPasswordError(Exception):
    pass

class OldServerVersion(Exception):
    pass

def main():
    """Run any commands via CLI interface"""
    try:
        server = sys.argv[1]
        if ':' in server:
            server, port = server.split(':')
        else:
            port = 4212

        command_name = sys.argv[2]
    except IndexError:
        print "usage: vlcclient.py server[:port] command [argument]"
        sys.exit(1)

    vlc = VLCClient(server, int(port))
    vlc.connect()
    print "Connected to VLC {0}".format(vlc.server_version)

    try:
        command = getattr(vlc, command_name)
        attr = sys.argv[2] if len(sys.argv) > 2 else None
        try:
            print command(attr)
        except TypeError:
            print command()
    except OldServerVersion as e:
        print "Error:", e

if __name__ == '__main__':
    main()
