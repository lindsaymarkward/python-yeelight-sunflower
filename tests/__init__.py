from yeelightsunflower.main import Hub, Bulb
import logging

# Setup logging
logger = logging.getLogger('yeelightsunflower')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

# TODO write more tests


def demo():
    hub = Hub()
    print("OK" if hub.available else "Not OK")

    bulbs = hub.get_lights()
    # bulbs[0].turn_off()

    light = get_bulb('3CB8', bulbs)
    if light is not None:
        print(light.available)
        light.set_rgb_color(0, 255, 255)
        # light.set_rgb_color(255, 0, 255)
        light.set_brightness(20)
        light.turn_off()
    else:
        print("Error getting light")


def get_bulb(zid, bulbs) -> Bulb:
    for bulb in bulbs:
        if bulb.zid == zid:
            return bulb


def test_hub():
    bad_hub = Hub('1.0.0.0')
    assert not bad_hub.available

demo()
test_hub()
