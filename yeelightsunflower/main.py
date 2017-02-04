import socket
import time

__author__ = 'Lindsay Ward'
GET_LIGHTS_COMMAND = "GLB,,,,0,\r\n"
BUFFER_SIZE = 8192


class Hub:
    # All Yeelight Sunflower bulbs are attached to the one hub
    def __init__(self, ip='192.168.1.59', port=10003):
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
        self._socket.send(command.encode("utf8"))
        return self.receive()

    def receive(self):
        """
        Receive a TCP response, looping to get the whole thing (or timeout)
        """
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
        response = self.send_command(GET_LIGHTS_COMMAND)
        # print("response: {}".format(response))
        if not response:
            return {}

        # deconstruct response string into light data
        # Example data: GLB 143E,1,1,25,255,255,255,0,0;287B,1,1,22,255,255,255,0,0;\r\n
        response = response[4:-3]  # strip start (GLB) and end (;\r\n)
        light_strings = response.split(';')
        light_data_by_id = {}
        for light_string in light_strings:
            values = light_string.split(',')
            try:
                light_data_by_id[values[0]] = [int(values[4]), int(values[5]), int(values[6]), int(values[7])]
            except ValueError:
                pass
        return light_data_by_id

    def get_lights(self):
        light_data = self.get_data()
        # print("get_data: {}".format(light_data))
        if not light_data:
            return False

        if self._bulbs:
            # Bulbs already created, just update values
            for bulb in self._bulbs:
                # use the values for the bulb with the correct ID
                values = light_data[bulb.id]
                bulb._r, bulb._g, bulb._b, bulb._level = values
        else:
            for light_id in light_data:
                self._bulbs.append(Bulb(self, light_id, *light_data[light_id]))
        # return a list of Bulb objects
        return self._bulbs

    def check(self):
        response = self.send_command("HB\r\n")
        return "HACK" in response


class Bulb:
    def __init__(self, hub, id, r, g, b, level):
        """
        The main controller class of a physical YeeLight Sunflower bulb.
        All bulbs share one hub
        :param id: The Zigbee ID of the bulb
        """
        self._hub = hub
        self._id = id
        self._r = int(r)
        self._g = int(g)
        self._b = int(b)
        self._level = int(level)

    @property
    def brightness(self):
        """ Return the brightness level"""
        return self._level

    @property
    def rgb_color(self):
        """Return the color property as list of [R, G, B], each 0-255"""
        return [self._r, self._g, self._b]

    @property
    def id(self):
        """ Return the bulb ID"""
        return self._id

    def turn_on(self):
        response = self._hub.send_command("C {},,,,100,\r\n".format(self._id))
        return response

    def turn_off(self):
        response = self._hub.send_command("C {},,,,0,\r\n".format(self._id))
        return response

    def set_rgb_color(self, r, g, b):
        response = self._hub.send_command("C {},{},{},{},,\r\n".format(self._id, r, g, b))
        return response

    def set_brightness(self, brightness):
        response = self._hub.send_command("C {},,,,{},\r\n".format(self._id, brightness))
        return response

    def is_on(self):
        return self._level > 0

    def update(self):
        self._hub.get_lights()
