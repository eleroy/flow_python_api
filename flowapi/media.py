import shutil
from typing import Literal
from flowapi.animation import Animation
from flowapi.items import Item


from PIL import Image
from pydantic import BaseModel, Field


import tempfile
from pathlib import Path

from flowapi.tools import FullPosition, PositionXYZ, RotationXYZ


class ValueTupleOfStringBooleanModel(BaseModel):
    Item1: str
    Item2: bool


class InternalHierarchyModel(BaseModel):
    ValueTupleOfStringBoolean: (
        list[ValueTupleOfStringBooleanModel] | ValueTupleOfStringBooleanModel
    )


class Media(Item):
    path: str | Path
    name: str = "Media"
    is_media: bool = True
    animation: Animation = Field(default_factory=Animation)
    animation_status: str = "OnceAndClamp"
    internal_hierarchy: InternalHierarchyModel | None = None
    root_content_path: str | None = Field(default=None)

    def model_post_init(self, __context):
        self.animation = Animation(media_path="Media\\" + Path(self.path).name)

    def set_path(self, path):
        self.path = path
        self.animation.media_path = "Media\\" + Path(self.path).name
        return self

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend(
            [
                {
                    "@xsi:type": "AnimationProperty",
                    "propertyIdentifier": "ItemPropertyAnimationIdentifier",
                    "title": "Animation",
                    "ItemIdentifier": {"Id": self.id},
                    "value": {
                        "animationIdentifier": {
                            "Id": self.animation.id,
                        },
                        "playAnimationStatus": self.animation_status,
                    },
                }
            ]
        )
        item_dict["PathInDatabase"] = "Media\\" + Path(self.path).name
        item_dict["InternalHierarchy"] = None
        if self.internal_hierarchy:
            item_dict["InternalHierarchy"] = self.internal_hierarchy.model_dump()
        if self.root_content_path:
            item_dict["RootContentPath"] = self.root_content_path
        return item_dict

    def set_width(self, width_m):
        self.set_scale(width_m, width_m, width_m)

    @staticmethod
    def get_placeholder(name: str = "Placeholder", type_file=".png"):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=type_file)
        path = Path(temp_file.name)
        image_placeholder = Image.new("RGB", (100, 100))
        image_placeholder.save(path, "PNG")
        return Media(path=path, name=name)


class AudioMedia(Media):
    play_shift: float = 36000
    volume: float = 100
    loop: bool = False

    def get_xml(self):
        xml = super().get_xml()
        xml["Properties"]["AbstractProperty"].extend(
            [
                {
                    "@xsi:type": "BoolProperty",
                    "propertyIdentifier": "Media_audio_loop_identifier",
                    "title": "Lire en boucle",
                    "ItemIdentifier": {"Id": self.id},
                    "value": self.loop,
                },
                {
                    "@xsi:type": "FloatProperty",
                    "propertyIdentifier": "Media_audio_volume_identifier",
                    "title": "Volume",
                    "ItemIdentifier": {"Id": self.id},
                    "value": self.volume,
                },
                {
                    "@xsi:type": "FloatProperty",
                    "propertyIdentifier": "Media_audio_decal_identifier",
                    "title": "Décalage de lecture (en secondes)",
                    "ItemIdentifier": {"Id": self.id},
                    "value": self.play_shift,
                },
            ]
        )
        return xml

    @staticmethod
    def get_placeholder(name: str = "AudioPlaceholder"):
        file_path = Path(__file__).parent.joinpath("sounds").joinpath("silence2s.mp3")
        return Media(path=file_path, name=name)

    @staticmethod
    def get_blip(
        name: str = "AudioBlip", blip_type: Literal["blip1", "blip2"] = "blip1"
    ):
        sound_directory = Path(__file__).parent.joinpath("sounds")
        if blip_type == "blip1":
            file_path = sound_directory.joinpath("blip.mp3")
        elif blip_type == "blip2":
            file_path = sound_directory.joinpath("blip2.mp3")
        return Media(path=file_path, name=name)


def parseMedia(
    medias,
    animations,
    media_id,
    scenario_path,
    saving_media_path=Path.cwd().joinpath("temp"),
):
    if not isinstance(medias["ArrayOfMediaMetadata"]["MediaMetadata"], list):
        media_data = [medias["ArrayOfMediaMetadata"]["MediaMetadata"]]
    else:
        media_data = medias["ArrayOfMediaMetadata"]["MediaMetadata"]
    media_ids = [c["ItemIdentifier"]["Id"] for c in media_data]
    comp_index = media_ids.index(media_id)
    comp_data = media_data[comp_index]
    saving_media_path.mkdir(exist_ok=True)
    origin_file = Path(scenario_path).joinpath(comp_data["PathInDatabase"])
    dest_file = saving_media_path.joinpath(origin_file.name)
    shutil.copyfile(origin_file, dest_file)
    new_component = Media(
        path=dest_file,
        id=comp_data["ItemIdentifier"]["Id"],
        is_active=comp_data["IsActive"],
        name=comp_data["Properties"]["AbstractProperty"][0]["value"],
        position=FullPosition(
            position=PositionXYZ.model_validate(
                comp_data["Properties"]["AbstractProperty"][1]["value"]["position"]
            ),
            rotation=RotationXYZ.from_euler_angles(
                PositionXYZ.model_validate(
                    comp_data["Properties"]["AbstractProperty"][1]["value"]["rotation"][
                        "eulerAngles"
                    ]
                )
            ),
            scale=PositionXYZ.model_validate(
                comp_data["Properties"]["AbstractProperty"][1]["value"]["scale"]
            ),
        ),
        internal_hierarchy=comp_data["InternalHierarchy"],
    )
    if "RootContentPath" in comp_data:
        new_component.root_content_path = comp_data["RootContentPath"]
    id_anim = comp_data["Properties"]["AbstractProperty"][2]["value"][
        "animationIdentifier"
    ]["Id"]
    if id_anim:
        animation = None
        for anim in animations["ArrayOfFlowAnimation"]["FlowAnimation"]:
            if anim["AnimationIdentifier"]["Id"] == id_anim:
                animation = Animation.parse(anim)
                break
        if animation is None:
            animation = Animation(id=id_anim)
    else:
        print("empty animation")
        animation = Animation()

    new_component.animation = animation
    new_component.set_path(dest_file)
    return new_component
