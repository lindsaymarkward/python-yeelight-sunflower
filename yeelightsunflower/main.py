"""
Python module for controlling Yeelight Sunflower bulbs.

This module exports the Hub and Bulb classes. All bulbs belong to one hub.
"""

import socket

__author__ = 'Lindsay Ward'
GET_LIGHTS_COMMAND = "GLB,,,,0,\r\n"
BUFFER_SIZE = 8192


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
        self._socket.settimeout(5)
        self._bulbs = []

        try:
            self._socket.connect((self._ip, self._port))
        except OSError:
            self._socket.close()

    def send_command(self, command):
        """Send TCP command to hub."""
        self._socket.send(command.encode("utf8"))
        return self.receive()

    def receive(self):
        """Receive TCP response, looping to get whole thing or timeout."""
        try:
            buf = self._socket.recv(BUFFER_SIZE)
        except socket.timeout:
            # Something is wrong, assume it's offline
            self._socket.close()
            return False

        # Read until a newline or timeout
        buffering = True
        response = ''
        while buffering:
            # print("buf: {}".format(buf))
            if '\n' in str(buf, 'utf-8'):
                response = str(buf, 'utf-8').split('\n')[0]
                buffering = False
            else:
                try:
                    more = self._socket.recv(BUFFER_SIZE)
                except socket.timeout:
                    more = None
                if not more:
                    buffering = False
                    response = str(buf, 'utf-8')
                else:
                    buf += more
        # print("in receive: {}".format(response))
        return response

    def get_data(self):
        """Get current light data as dictionary with light zids as keys."""
        response = self.send_command(GET_LIGHTS_COMMAND)
        # print("response: {}".format(response))
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
                light_data_by_id[values[0]] = [int(values[4]), int(values[5]),
                                               int(values[6]), int(values[7])]
            except ValueError:
                print("*** Value error: {}".format(values))
                # pass
            except IndexError:
                print("*** Index error: {}".format(values))
                # pass
        return light_data_by_id

    def get_lights(self):
        """Get current light data, set and return as list of Bulb objects."""
        light_data = self.get_data()
        # print("get_data: {}".format(light_data))
        if not light_data:
            return False

        if self._bulbs:
            # Bulbs already created, just update values
            for bulb in self._bulbs:
                # use the values for the bulb with the correct ID
                try:
                    values = light_data[bulb.zid]
                    bulb._r, bulb._g, bulb._b, bulb._level = values
                except KeyError:
                    pass
        else:
            for light_id in light_data:
                self._bulbs.append(Bulb(self, light_id, *light_data[light_id]))
        # return a list of Bulb objects
        return self._bulbs

    def check(self):
        """Check if hub is responsive."""
        response = self.send_command("HB\r\n")
        return "HACK" in response


class Bulb:
    """
    Yeelight Bulb object.

    Data and methods for light color and brightness. Requires Hub.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, hub, zid, red, green, blue, level):
        # pylint: enable=too-many-arguments
        """Construct a Bulb (light) based on current values."""
        self._hub = hub
        self._zid = zid
        self._red = int(red)
        self._green = int(green)
        self._blue = int(blue)
        self._level = int(level)

    @property
    def brightness(self):
        """Return the brightness level."""
        return self._level

    @property
    def rgb_color(self):
        """Return the color property as list of [R, G, B], each 0-255."""
        return [self._red, self._green, self._blue]

    @property
    def zid(self):
        """Return the bulb ID."""
        return self._zid

    def turn_on(self):
        """Turn bulb on (full brightness)."""
        response = self._hub.send_command("C {},,,,100,\r\n".format(self._zid))
        print("Turn on {}".format(response))
        return response

    def turn_off(self):
        """Turn bulb off (zero brightness)."""
        response = self._hub.send_command("C {},,,,0,\r\n".format(self._zid))
        print("Turn off {}".format(response))
        return response

    def set_rgb_color(self, red, green, blue):
        """Set color of bulb."""
        response = self._hub.send_command(
            "C {},{},{},{},,\r\n".format(self._zid, red, green, blue))
        print("Set RGB {}".format(response))
        return response

    def set_brightness(self, brightness):
        """Set brightness of bulb."""
        response = self._hub.send_command(
            "C {},,,,{},\r\n".format(self._zid, brightness))
        print("Set brightness {}".format(response))
        return response

    def set_all(self, red, green, blue, brightness):
        """Set color and brightness of bulb."""
        response = self._hub.send_command(
            "C {},{},{},{},{},\r\n".format(self._zid, red, green, blue,
                                           brightness))
        print("Set all {}".format(response))
        return response

    def is_on(self):
        """Determine if bulb is on (brightness not zero)."""
        return self._level > 0

    def update(self):
        """Update light objects to their current values."""
        self._hub.get_lights()
