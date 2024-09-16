'''import carla
import random
from carla_birdeye_view import BirdViewProducer, BirdViewCropType, PixelDimensions

client = carla.Client('127.0.0.1', 2000)
world = client.get_world()
map = world.get_map()
spawn_points = map.get_spawn_points()


blueprints = world.get_blueprint_library()
hero_bp = random.choice(blueprints.filter("vehicle.audi.a2"))
hero_bp.set_attribute("role_name", "hero")
transform = random.choice(spawn_points)
agent = world.spawn_actor(hero_bp, transform)
agent.set_autopilot(True)

birdview_producer = BirdViewProducer(
    client,     
    target_size=PixelDimensions(width=500, height=500),
    pixels_per_meter=4,
    crop_type=BirdViewCropType.FRONT_AND_REAR_AREA
)

birdview = birdview_producer.produce(
        agent_vehicle=agent
)

rgb = BirdViewProducer.as_rgb(birdview)'''


import carla
import math
import random

from cv2 import cv2 as cv
from carla_birdeye_view import (
    BirdViewProducer,
    BirdView,
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    BirdViewCropType,
)
from carla_birdeye_view.mask import PixelDimensions

STUCK_SPEED_THRESHOLD_IN_KMH = 3
MAX_STUCK_FRAMES = 500000


def get_speed(actor: carla.Actor) -> float:
    """in km/h"""
    vector: carla.Vector3D = actor.get_velocity()
    MPS_TO_KMH = 3.6
    return MPS_TO_KMH * math.sqrt(vector.x ** 2 + vector.y ** 2 + vector.z ** 2)


def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(3.0)
    world = client.get_world()
    map = world.get_map()
    spawn_points = map.get_spawn_points()
    blueprints = world.get_blueprint_library()

    # settings = world.get_settings()
    # settings.synchronous_mode = True
    # settings.no_rendering_mode = True
    # settings.fixed_delta_seconds = 1 / 10.0
    # world.apply_settings(settings)

    hero_bp = random.choice(blueprints.filter("vehicle.audi.a2"))
    hero_bp.set_attribute("role_name", "hero")
    transform = random.choice(spawn_points)
    agent = world.spawn_actor(hero_bp, transform)
    agent.set_autopilot(True)

    birdview_producer = BirdViewProducer(
        client,
        PixelDimensions(width=1000, height=1000),
        pixels_per_meter=4,
        crop_type=BirdViewCropType.FRONT_AND_REAR_AREA,
    )
    stuck_frames_count = 0

    while True:
        # world.tick()
        
        # Create the bird's eye view frame
        birdview: BirdView = birdview_producer.produce(agent_vehicle=agent)
        
        # Create the speedometer view frame
        
        
        bgr = cv.cvtColor(BirdViewProducer.as_rgb(birdview), cv.COLOR_BGR2RGB)
        # NOTE imshow requires BGR color model
        cv.imshow("BirdView RGB", bgr)

        # Teleport when stuck for too long
        if get_speed(agent) < STUCK_SPEED_THRESHOLD_IN_KMH:
            stuck_frames_count += 1
        else:
            stuck_frames_count = 0

        if stuck_frames_count == MAX_STUCK_FRAMES:
            agent.set_autopilot(False)
            print('STUCK FRAMES')
            agent.set_transform(random.choice(spawn_points))
            agent.set_autopilot(True)

        # Play next frames without having to wait for the key
        key = cv.waitKey(10) & 0xFF
        if key == 27:  # ESC
            break
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
