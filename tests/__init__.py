from yeelightsunflower.main import Hub, Bulb

# TODO write more tests


def demo():
    hub = Hub()
    print("OK" if hub.check() else "Not OK")

    bulbs = hub.get_lights()
    bulbs[0].turn_off()

demo()