# coding: utf-8
"""
    VLCClient
    ~~~~~~~~~

    This module allows to control a VLC instance through a python interface.

    You need to enable the telnet interface, e.g. start
    VLC like this:

    $ vlc --intf telnet --telnet-password admin

    To start VLC with allowed remote admin:
    $ vlc --intf telnet --telnet-password admin \
      --lua-config "telnet={host='0.0.0.0:4212'}"

    Replace --intf with --extraintf to start telnet and the regular GUI

    More information about the telnet interface:
    http://wiki.videolan.org/Documentation:Streaming_HowTo/VLM

    :author: Michael Mayr <michael@dermitch.de>
    :licence: MIT License
    :version: 0.2.0
"""

from __future__ import print_function

import sys
import inspect
import telnetlib

DEFAULT_PORT = 4212


class VLCClient(object):
    """
    Connection to a running VLC instance with telnet interface.
    """

    def __init__(self, server, port=DEFAULT_PORT, password="admin", timeout=5):
        self.server = server
        self.port = port
        self.password = password
        self.timeout = timeout

        self.telnet = None
        self.server_version = None
        self.server_version_tuple = ()

    def connect(self):
        """
        Connect to VLC and login
        """
        assert self.telnet is None, "connect() called twice"

        self.telnet = telnetlib.Telnet()
        self.telnet.open(self.server, self.port, self.timeout)

        # Parse version
        result = self.telnet.expect([
            r"VLC media player ([\d.]+)".encode("utf-8"),
        ])
        self.server_version = result[1].group(1)
        self.server_version_tuple = self.server_version.decode("utf-8").split('.')

        # Login
        self.telnet.read_until("Password: ".encode("utf-8"))
        self.telnet.write(self.password.encode("utf-8"))
        self.telnet.write("\n".encode("utf-8"))

        # Password correct?
        result = self.telnet.expect([
            "Password: ".encode("utf-8"),
            ">".encode("utf-8")
        ])
        if "Password".encode("utf-8") in result[2]:
            raise WrongPasswordError()

    def disconnect(self):
        """
        Disconnect and close connection
        """
        self.telnet.close()
        self.telnet = None

    def _send_command(self, line):
        """
        Sends a command to VLC and returns the text reply.
        This command may block.
        """
        self.telnet.write((line + "\n").encode("utf-8"))
        return self.telnet.read_until(">".encode("utf-8"))[1:-3]

    def _require_version(self, command, version):
        """
        Check if the server runs at least at a specific version
        or raise an error.
        """
        if isinstance(version, basestring):
            version = version.split('.')
        if version > self.server_version_tuple:
            raise OldServerVersion(
                "Command '{0} requires at least VLC {1}".format(
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

    def set_fullscreen(self, value):
        """set fullscreen on or off"""
        assert type(value) is bool
        return self._send_command("fullscreen {}".format("on" if value else "off"))

    def raw(self, *args):
        """
        Send a raw telnet command
        """
        return self._send_command(" ".join(args))

    #
    # Playlist
    #
    def add(self, filename):
        """
        Add a file to the playlist and play it.
        This command always succeeds.
        """
        return self._send_command('add {0}'.format(filename))

    def enqueue(self, filename):
        """
        Add a file to the playlist. This command always succeeds.
        """
        return self._send_command("enqueue {0}".format(filename))

    def seek(self, second):
        """
        Jump to a position at the current stream if supported.
        """
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

    def loop(self):
        """Toggle loop"""
        return self._send_command("loop")

    def repeat(self):
        """Toggle repeat of a single item"""
        return self._send_command("repeat")

    def random(self):
        """Toggle random playback"""
        return self._send_command("random")

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
    """Invalid password sent to the server."""
    pass


class OldServerVersion(Exception):
    """VLC version is too old for the requested commmand."""
    pass


def main():
    """
    Run any commands via CLI interface
    """
    try:
        server = sys.argv[1]
        if ':' in server:
            server, port = server.split(':')
        else:
            port = DEFAULT_PORT

        command_name = sys.argv[2]
    except IndexError:
        print("usage: vlcclient.py server[:port] command [argument]",
              file=sys.stderr)
        sys.exit(1)

    vlc = VLCClient(server, int(port))
    vlc.connect()
    print("Connected to VLC {0}\n".format(vlc.server_version),
          file=sys.stderr)

    try:
        command = getattr(vlc, command_name)
        argspec = inspect.getargspec(command)
        cli_args = sys.argv[3:]
        cmd_args = argspec.args[1:]

        if not argspec.varargs and len(cli_args) != len(cmd_args):
            print("Error: {} requires {} arguments, but only got {}".format(
                command_name, len(cmd_args), len(cli_args),
            ), file=sys.stderr)
            exit(1)

        result = command(*cli_args)
        print(result)

    except OldServerVersion as exc:
        print("Error: {0}\n".format(exc), file=sys.stderr)

if __name__ == '__main__':
    main()
