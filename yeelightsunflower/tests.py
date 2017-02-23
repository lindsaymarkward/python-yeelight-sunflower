"""Tests for yeelightsunflower library."""

import logging
import time
from yeelightsunflower.main import Hub

ZID_TO_TEST = '3CB8'
SECONDS_TO_WAIT = 2.95

# Setup logging
LOGGER = logging.getLogger('yeelightsunflower')
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler())


# TODO write more tests


def test_hub():
    """Test Hub with basic testable things."""
    bad_hub = Hub('1.0.0.0')
    assert not bad_hub.available


def demo():
    """Demo some specific functionality. Needs to be customised."""
    hub = Hub()
    if hub.available:
        LOGGER.info("Successfully created Hub")
    else:
        LOGGER.info("Could not create Hub")

    bulbs = hub.get_lights()

    # Enter zid of bulb to test, or use the line below this to get first one
    light = get_bulb(ZID_TO_TEST, bulbs)
    # light = bulbs[0]
    if light is not None:
        if light.available:
            LOGGER.info("Light is available")
            assert light.available
            light.turn_on()
            time.sleep(SECONDS_TO_WAIT)
            assert light.is_on
            light.update()
            light.update()
            # light.set_rgb_color(255, 0, 255)
            light.set_rgb_color(0, 255, 255)
            time.sleep(SECONDS_TO_WAIT)
            light.update()
            assert light.rgb_color == [0, 255, 255]
            light.set_brightness(42)
            time.sleep(SECONDS_TO_WAIT)
            assert light.brightness == 42
            assert light.is_on
            light.turn_off()
            time.sleep(SECONDS_TO_WAIT)
            assert not light.is_on
            light.set_all(128, 129, 130, 92)
            time.sleep(SECONDS_TO_WAIT)
            LOGGER.info("Current values: %s at %s", light.rgb_color,
                        light.brightness)
            assert light.brightness == 92
            assert light.rgb_color == [128, 129, 130]
            light.turn_off()
        else:
            LOGGER.info("Light is not available")
    else:
        LOGGER.error("Error getting light")


def get_bulb(zid, bulbs):
    """Retrieve a bulb by its zid from a list of Bulb objects."""
    for bulb in bulbs:
        if bulb.zid == zid:
            return bulb


# demo()
test_hub()
