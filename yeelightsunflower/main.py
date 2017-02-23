"""
Python module for controlling Yeelight Sunflower bulbs.

This module exports the Hub and Bulb classes. All bulbs belong to one hub.
"""

import datetime
import logging
import socket
import threading

GET_LIGHTS_COMMAND = "GL,,,,0,\r\n"
BUFFER_SIZE = 8192
UPDATE_INTERVAL_SECONDS = 1
_LOGGER = logging.getLogger(__name__)


class Hub:
    """
    Yeelight Hub object.

    All Yeelight Sunflower bulbs are attached to the one hub.
    Hub uses TCP sockets to send and receive light data.
    """

    def __init__(self, ip='192.168.1.59', port=10003):
        """Create a hub with given IP and port, establishing socket."""
        self._port = port
        self._ip = ip
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(4)
        self._bulbs = []
        self._lock = threading.Lock()
        # set last updated time to old time so first update will happen
        self._last_updated = datetime.datetime.now() - datetime.timedelta(
            seconds=30)

        try:
            self._socket.connect((self._ip, self._port))
        except socket.error as error:
            _LOGGER.error("Error creating Hub: %s", error)
            self._socket.close()

    def send_command(self, command):
        """Send TCP command to hub."""
        # use lock to make TCP send/receive thread safe
        with self._lock:
            try:
                self._socket.send(command.encode("utf8"))
                result = self.receive()
                # hub may send "status"/"new" messages that should be ignored
                while result.startswith("S") or result.startswith("NEW"):
                    # _LOGGER.info("!Got status response: %s", result)
                    result = self.receive()
                _LOGGER.debug("Received: %s", result)
                return result
            except socket.error as error:
                _LOGGER.error("Error sending command: %s", error)
                return ""

    def receive(self):
        """Receive TCP response, looping to get whole thing or timeout."""
        try:
            buf = self._socket.recv(BUFFER_SIZE)
        except socket.timeout as error:
            # Something is wrong, assume it's offline
            _LOGGER.error("Error receiving: %s", error)
            self._socket.close()
            return False

        # Read until a newline or timeout
        buffering = True
        response = ''
        while buffering:
            if '\n' in buf.decode("utf8"):
                response = buf.decode("utf8").split('\n')[0]
                buffering = False
            else:
                try:
                    more = self._socket.recv(BUFFER_SIZE)
                except socket.timeout:
                    more = None
                if not more:
                    buffering = False
                    response = buf.decode("utf8")
                else:
                    buf += more
        return response

    def get_data(self):
        """Get current light data as dictionary with light zids as keys."""
        response = self.send_command(GET_LIGHTS_COMMAND)
        _LOGGER.debug("get_data response: %s", response)
        if not response:
            return {}

        # deconstruct response string into light data. Example data:
        # GLB 143E,1,1,25,255,255,255,0,0;287B,1,1,22,255,255,255,0,0;\r\n
        response = response[4:-3]  # strip start (GLB) and end (;\r\n)
        light_strings = response.split(';')
        light_data_by_id = {}
        for light_string in light_strings:
            values = light_string.split(',')
            try:
                light_data_by_id[values[0]] = [int(values[2]), int(values[4]),
                                               int(values[5]), int(values[6]),
                                               int(values[7])]
            except ValueError as error:
                _LOGGER.error("Error %s: %s (%s)", error, values, response)
            except IndexError as error:
                _LOGGER.error("Error %s: %s (%s)", error, values, response)
        return light_data_by_id

    def get_lights(self):
        """Get current light data, set and return as list of Bulb objects."""
        # Throttle updates. Use cached data if within UPDATE_INTERVAL_SECONDS
        now = datetime.datetime.now()
        if (now - self._last_updated) < datetime.timedelta(
                seconds=UPDATE_INTERVAL_SECONDS):
            _LOGGER.debug("Using cached light data")
            return self._bulbs
        else:
            self._last_updated = now

        light_data = self.get_data()
        _LOGGER.debug("got: %s", light_data)
        if not light_data:
            return []

        if self._bulbs:
            # Bulbs already created, just update values
            for bulb in self._bulbs:
                # use the values for the bulb with the correct ID
                try:
                    values = light_data[bulb.zid]
                    bulb._online, bulb._red, bulb._green, bulb._blue, \
                        bulb._level = values
                except KeyError:
                    pass
        else:
            for light_id in light_data:
                self._bulbs.append(Bulb(self, light_id, *light_data[light_id]))
        # return a list of Bulb objects
        return self._bulbs

    @property
    def available(self):
        """Check if hub is responsive."""
        response = self.send_command("HB\r\n")
        return "HACK" in response


class Bulb:
    """
    Yeelight Bulb object.

    Data and methods for light color and brightness. Requires Hub.
    """

    def __init__(self, hub, zid, online, red, green, blue, level):
        """Construct a Bulb (light) based on current values."""
        self._hub = hub
        self._zid = zid
        self._online = online == 1  # online = 1, offline = 0
        self._red = int(red)
        self._green = int(green)
        self._blue = int(blue)
        self._level = int(level)

    @property
    def brightness(self):
        """Return the brightness level."""
        self.update()
        return self._level

    @property
    def rgb_color(self):
        """Return the color property as list of [R, G, B], each 0-255."""
        self.update()
        return [self._red, self._green, self._blue]

    @property
    def zid(self):
        """Return the bulb ID."""
        return self._zid

    @property
    def available(self):
        """Return True if this bulb is online in the current list of bulbs."""
        self.update()
        return self._online

    @property
    def is_on(self):
        """Determine if bulb is on (brightness not zero)."""
        self.update()
        return self._level > 0

    def turn_on(self):
        """Turn bulb on (full brightness)."""
        command = "C {},,,,100,\r\n".format(self._zid)
        response = self._hub.send_command(command)
        _LOGGER.debug("Turn on %s: %s", repr(command), response)
        return response

    def turn_off(self):
        """Turn bulb off (zero brightness)."""
        command = "C {},,,,0,\r\n".format(self._zid)
        response = self._hub.send_command(command)
        _LOGGER.debug("Turn off %s: %s", repr(command), response)
        return response

    def set_rgb_color(self, red, green, blue):
        """Set color of bulb."""
        command = "C {},{},{},{},,\r\n".format(self._zid, red, green, blue)
        response = self._hub.send_command(command)
        _LOGGER.debug("Set RGB %s: %s", repr(command), response)
        return response

    def set_brightness(self, brightness):
        """Set brightness of bulb."""
        command = "C {},,,,{},\r\n".format(self._zid, brightness)
        response = self._hub.send_command(command)
        _LOGGER.debug("Set brightness %s: %s", repr(command), response)
        return response

    def set_all(self, red, green, blue, brightness):
        """Set color and brightness of bulb."""
        command = "C {},{},{},{},{},\r\n".format(self._zid, red, green, blue,
                                                 brightness)
        response = self._hub.send_command(command)
        _LOGGER.debug("Set all %s: %s", repr(command), response)
        return response

    def update(self):
        """Update light objects to their current values."""
        self._hub.get_lights()
