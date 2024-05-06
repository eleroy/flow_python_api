import math
from pathlib import Path
import uuid
uuid_list = set()
global_scenario_path = Path("Scenarios")
temp_image_path = Path("temp_images")

def get_quaternion_from_euler(eulerAngles):
    """
    Convert an Euler angle to a quaternion.

    Input
      :param roll: The roll (rotation around x-axis) angle in radians.
      :param pitch: The pitch (rotation around y-axis) angle in radians.
      :param yaw: The yaw (rotation around z-axis) angle in radians.

    Output
      :return qx, qy, qz, qw: The orientation in quaternion [x,y,z,w] format
    """
    roll = float(eulerAngles["x"]) * math.pi / 180
    pitch = float(eulerAngles["y"]) * math.pi / 180
    yaw = float(eulerAngles["z"]) * math.pi / 180
    qx = math.sin(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) - math.cos(roll / 2) * math.sin(
        pitch / 2) * math.sin(yaw / 2)
    qy = math.cos(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.cos(
        pitch / 2) * math.sin(yaw / 2)
    qz = math.cos(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2) - math.sin(roll / 2) * math.sin(
        pitch / 2) * math.cos(yaw / 2)
    qw = math.cos(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.sin(
        pitch / 2) * math.sin(yaw / 2)

    return {"x": -qx, "y": -qy, "z": -qz, "w": -qw}


def get_uuid():
    global uuid_list
    for i in range(20):
        new_uuid = str(uuid.uuid4())[:8]
        if new_uuid not in uuid_list:
            break
    uuid_list.add(new_uuid)
    return f'{new_uuid}'

def clear_uuid_database():
    global uuid_list
    uuid_list = set()