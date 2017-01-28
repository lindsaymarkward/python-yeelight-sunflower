import socket
import time

GET_LIGHTS_COMMAND = "GLB,,,,0,\r\n"

__author__ = 'Lindsay Ward'

BUFFER_SIZE = 8192


class Hub:
    # All Yeelight Sunflower bulbs are attached to the one hub
    def __init__(self, ip='192.168.1.59', port=10003):
        self._port = port
        self._ip = ip
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._bulbs = []

        # def connect(self):
        # TODO: add error handling
        self._socket.connect((self._ip, self._port))

    def send_command(self, command):
        self._socket.send(command.encode("utf8"))
        return self._receive()

    def _receive(self, timeout=2):
        # make socket non-blocking
        self._socket.setblocking(0)

        # total data partwise in an array
        total_data = []

        # beginning time
        begin = time.time()
        while True:
            # if you got some data, then break after timeout
            if total_data and time.time() - begin > timeout:
                break

            # if you got no data at all, wait a little longer, twice the timeout
            elif time.time() - begin > timeout * 2:
                break

            # _receive something
            try:
                data = self._socket.recv(BUFFER_SIZE)
                # print("Got: ", repr(data))
                if data:
                    total_data.append(data.decode())
                    # change the beginning time for measurement
                    begin = time.time()
                else:
                    # sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass

        # join all parts to make final string
        return ''.join(total_data)

    def get_lights(self):
        # TODO: (?? not sure about this)
        self._bulbs = []  # clear existing bulbs

        response = self.send_command(GET_LIGHTS_COMMAND)
        # deconstruct response string into light data
        # Example data: GLB 143E,1,1,25,255,255,255,0,0;287B,1,1,22,255,255,255,0,0;\r\n
        response = response[4:-3]  # strip start (GLB) and end (;\r\n)
        light_strings = response.split(';')
        for light_string in light_strings:
            values = light_string.split(',')
            data = (values[0], values[4], values[5], values[6], values[7])
            self._bulbs.append(Bulb(self, *data))
            # print(data)
        # print(self._bulbs)
        return self._bulbs

    def check(self):
        response = self.send_command("HB\r\n")
        return response == "HACK\r\n"


class Bulb:
    def __init__(self, hub, id, r, g, b, level):
        """
        The main controller class of a physical YeeLight Sunflower bulb.
        All bulbs share one hub
        :param id: The Zigbee ID of the bulb
        """
        self._hub = hub
        self._id = id
        self._r = r
        self._g = g
        self._b = b
        self._level = level

    def turn_on(self):
        response = self._hub.send_command("C {},,,,100,\r\n".format(self._id))
        return response

    def turn_off(self):
        response = self._hub.send_command("C {},,,,0,\r\n".format(self._id))
        return response


def demo():
    hub = Hub()
    print("OK" if hub.check() else "Not OK")

    bulbs = hub.get_lights()
    bulbs[0].turn_off()


demo()
