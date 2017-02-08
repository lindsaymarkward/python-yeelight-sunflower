from yeelightsunflower.main import Hub, Bulb

# TODO write more tests


def demo():
    hub = Hub()
    print("OK" if hub.check() else "Not OK")

    bulbs = hub.get_lights()
    # bulbs[0].turn_off()

    light = get_bulb('3CB8', bulbs)
    # light.turn_off()

    light.set_rgb_color(0, 255, 255)
    # light.set_rgb_color(255, 0, 255)
    light.set_brightness(20)


def get_bulb(zid, bulbs) -> Bulb:
    for bulb in bulbs:
        if bulb.zid == zid:
            return bulb


demo()
