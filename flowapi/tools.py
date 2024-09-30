import math
from pathlib import Path
import uuid
from pydantic import BaseModel, Field

uuid_list = set()
global_scenario_path = Path("Scenarios")
temp_image_path = Path("temp_images")


class PositionXYZ(BaseModel):
    x: float = 0
    y: float = 0
    z: float = 0


class RotationXYZ(BaseModel):
    x: float = 0
    y: float = 0
    z: float = 0
    w: float = 1
    eulerAngles: PositionXYZ = Field(default_factory=PositionXYZ)

    def set_rotation_angles(self, rotation_euler_angles: PositionXYZ):
        full_rotation = get_quaternion_from_euler(rotation_euler_angles)
        self.x = full_rotation.x
        self.y = full_rotation.y
        self.z = full_rotation.z
        self.w = full_rotation.w
        self.eulerAngles = rotation_euler_angles

    @staticmethod
    def from_euler_angles(eulerAngles: PositionXYZ):
        rot = RotationXYZ()
        rot.set_rotation_angles(eulerAngles)
        return rot


class FullPosition(BaseModel):
    position: PositionXYZ = Field(default_factory=PositionXYZ)
    rotation: RotationXYZ = Field(default_factory=RotationXYZ)
    scale: PositionXYZ = Field(default_factory=lambda: PositionXYZ(x=1, y=1, z=1))

    def set_rotation_angles(self, rotation_euler_angles: PositionXYZ):
        self.rotation = get_quaternion_from_euler(rotation_euler_angles)


def get_quaternion_from_euler(eulerAngles: PositionXYZ) -> RotationXYZ:
    """
    Convert an Euler angle to a quaternion.

    Input
      :param roll: The roll (rotation around x-axis) angle in radians.
      :param pitch: The pitch (rotation around y-axis) angle in radians.
      :param yaw: The yaw (rotation around z-axis) angle in radians.

    Output
      :return qx, qy, qz, qw: The orientation in quaternion [x,y,z,w] format
    """
    roll = float(eulerAngles.x) * math.pi / 180
    pitch = float(eulerAngles.y) * math.pi / 180
    yaw = float(eulerAngles.z) * math.pi / 180
    qx = math.sin(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) - math.cos(
        roll / 2
    ) * math.sin(pitch / 2) * math.sin(yaw / 2)
    qy = math.cos(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2) + math.sin(
        roll / 2
    ) * math.cos(pitch / 2) * math.sin(yaw / 2)
    qz = math.cos(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2) - math.sin(
        roll / 2
    ) * math.sin(pitch / 2) * math.cos(yaw / 2)
    qw = math.cos(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) + math.sin(
        roll / 2
    ) * math.sin(pitch / 2) * math.sin(yaw / 2)

    return RotationXYZ(x=qx, y=qy, z=qz, w=qw, eulerAngles=eulerAngles)


def get_uuid():
    global uuid_list
    for i in range(20):
        new_uuid = str(uuid.uuid4())[:8]
        if new_uuid not in uuid_list:
            break
    uuid_list.add(new_uuid)
    return f"{new_uuid}"


def clear_uuid_database():
    global uuid_list
    uuid_list = set()


def look_in_table(table, child_key, value):
    for item in table:
        if child_key in item:
            if item[child_key] == value:
                return item
    return False


if __name__ == "__main__":
    pos = FullPosition()
    print(pos)
