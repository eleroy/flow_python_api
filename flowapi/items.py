import copy
import shutil
from pathlib import Path

from pydantic import BaseModel, Field

from .animation import Animation
from .tools import (
    FullPosition,
    PositionXYZ,
    RotationXYZ,
    get_uuid,
    get_quaternion_from_euler,
)
import tempfile
from PIL import Image


class Item(BaseModel):
    name: str
    id: str = Field(default_factory=get_uuid)
    is_media: bool = False
    is_active: bool = True
    position: FullPosition = Field(default_factory=FullPosition)

    def get_item_xml(self):
        item_dict = {
            "ItemIdentifier": {"Id": self.id},
            "IsActive": self.is_active,
            "Properties": {
                "AbstractProperty": [
                    {
                        "@xsi:type": "ShortStringProperty",
                        "propertyIdentifier": "ItemPropertyInstanceIdentifier",
                        "title": "Identifiant",
                        "ItemIdentifier": {"Id": self.id},
                        "value": self.name,
                        "AllowEmpty": False,
                    },
                    {
                        "@xsi:type": "TransformProperty",
                        "propertyIdentifier": "ItemPropertyTransformIdentifier",
                        "title": "Position, rotation &amp; échelle",
                        "ItemIdentifier": {"Id": self.id},
                        "value": self.position.model_dump(),
                    },
                ]
            },
        }
        return item_dict

    def get_xml(self):
        return self.get_item_xml()

    def set_position(self, x=None, y=None, z=None):
        if x:
            self.position.position.x = x
        if y:
            self.position.position.y = y
        if z:
            self.position.position.z = z
        return self

    def set_rotation(self, x=None, y=None, z=None):
        current_rotation = self.position.rotation.eulerAngles
        if x:
            current_rotation.x = x
        if y:
            current_rotation.y = y
        if z:
            current_rotation.z = z
        self.position.set_rotation_angles(current_rotation)
        return self

    def set_scale(self, x=None, y=None, z=None):
        if x:
            self.position.scale.x = x
        if y:
            self.position.scale.y = y
        if z:
            self.position.scale.z = z
        return self

    def clone(self):
        new_item = copy.copy(self)
        new_item.id = get_uuid()
        return new_item


class Component(Item):
    property_identifier: str = ""
    nov_component_identifier: str = ""
    to: str | None = None

    def parse(self, component_dict):
        pass

    def get_xml(self):
        component_dict = {
            "ItemIdentifier": {"Id": self.id},
            "IsActive": self.is_active,
            "Properties": {"AbstractProperty"},
        }
        return component_dict

    def target(self, dest_step_id):
        if hasattr(dest_step_id, "id"):
            self.to = dest_step_id.id
        else:
            self.to = dest_step_id
        return self


class BoutonText(Component):
    name: str = "Bouton texte"
    value: str = "Click"
    property_identifier: str = "Component_button_text_interactive_identifier"
    base_width_m: float = 0.15
    nov_component_identifier: str = "Component_button_text"

    def parse(self, component_dict):
        self.value = component_dict["Properties"]["AbstractProperty"][2]["value"]

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend(
            [
                {
                    "@xsi:type": "ShortStringProperty",
                    "propertyIdentifier": "Component_button_text_identifier",
                    "title": "Texte",
                    "ItemIdentifier": {"Id": self.id},
                    "value": self.value,
                    "AllowEmpty": False,
                },
                {
                    "@xsi:type": "InteractiveProperty",
                    "propertyIdentifier": self.property_identifier,
                    "title": "Bouton suivant",
                    "ItemIdentifier": {"Id": self.id},
                    "value": {
                        "displayInProperties": False,
                        "interactiveDirection": "Next",
                        "isActive": True,
                    },
                },
            ]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict

    def set_size(self, diameter_m):
        self.set_scale(
            diameter_m / self.base_width_m,
            diameter_m / self.base_width_m,
            diameter_m / self.base_width_m,
        )
        return self


class Media(Item):
    path: str | Path
    name: str = "Media"
    is_media: bool = True
    animation: Animation = Field(default_factory=Animation)
    animation_status: str = "OnceAndClamp"

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
                        "animationIdentifier": {"Id": self.animation.id},
                        "playAnimationStatus": self.animation_status,
                    },
                }
            ]
        )
        item_dict["PathInDatabase"] = "Media\\" + Path(self.path).name
        item_dict["InternalHierarchy"] = None
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


class BoutonSimple(Component):
    name: str = "Bouton simple"
    property_identifier: str = "Component_button_simple_interactive_identifier"
    base_width_m: float = 0.15
    nov_component_identifier: str = "Component_button_simple"

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend(
            [
                {
                    "@xsi:type": "InteractiveProperty",
                    "propertyIdentifier": self.property_identifier,
                    "title": "Bouton suivant",
                    "ItemIdentifier": {"Id": self.id},
                    "value": {
                        "displayInProperties": False,
                        "interactiveDirection": "Next",
                        "isActive": True,
                    },
                }
            ]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict

    def set_size(self, diameter_m):
        self.set_scale(
            diameter_m / self.base_width_m,
            diameter_m / self.base_width_m,
            diameter_m / self.base_width_m,
        )
        return self


class Timer(Component):
    duration: float
    name: str = "Timer"
    property_identifier: str = "Component_timer_interactive_identifier"
    nov_component_identifier: str = "Component_timer"

    def parse(self, component_dict):
        self.duration = float(
            component_dict["Properties"]["AbstractProperty"][2]["value"]
        )
        return self

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend(
            [
                {
                    "@xsi:type": "FloatProperty",
                    "AllowEmpty": "false",
                    "ItemIdentifier": {"Id": self.id},
                    "propertyIdentifier": "Component_timer_duration_identifier",
                    "title": "Durée (en secondes)",
                    "value": f"{self.duration}",
                },
                {
                    "@xsi:type": "InteractiveProperty",
                    "propertyIdentifier": self.property_identifier,
                    "title": "Étape suivante",
                    "ItemIdentifier": {"Id": self.id},
                    "value": {
                        "displayInProperties": False,
                        "interactiveDirection": "Next",
                        "isActive": True,
                    },
                },
            ]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict


class Zone(Component):
    name: str = "Zone"
    property_identifier: str = "Component_zone_interactive_identifier"
    nov_component_identifier: str = "Component_zone"

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend(
            [
                {
                    "@xsi:type": "InteractiveProperty",
                    "propertyIdentifier": self.property_identifier,
                    "title": "Étape suivante",
                    "ItemIdentifier": {"Id": self.id},
                    "value": {
                        "displayInProperties": False,
                        "interactiveDirection": "Next",
                        "isActive": True,
                    },
                }
            ]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict


class Texte(Component):
    name: str = "Texte"
    property_identifier: str = "Component_zone_interactive_identifier"
    value: str = "Texte"
    base_width_m: float = 1
    nov_component_identifier: str = "Component_text"

    def parse(self, component_dict):
        self.value = component_dict["Properties"]["AbstractProperty"][2]["value"]

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend(
            [
                {
                    "@xsi:type": "LongStringProperty",
                    "AllowEmpty": "false",
                    "ItemIdentifier": {"Id": self.id},
                    "propertyIdentifier": "Component_text_description_identifier",
                    "title": "Texte",
                    "value": self.value,
                }
            ]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict

    def set_size(self, diameter_m):
        self.set_scale(
            diameter_m / self.base_width_m,
            diameter_m / self.base_width_m,
            diameter_m / self.base_width_m,
        )
        return self


class Panneau(Component):
    name: str = "Panneau"
    titre: str = "Title"
    description: str = "Description"
    image: str | None = None
    property_identifier: str = (
        "Component_panel_formation_button_next_interactive_identifier"
    )
    base_width_m: float = 1
    nov_component_identifier: str = "Component_panel_formation"

    def parse(self, component_dict):
        self.titre = component_dict["Properties"]["AbstractProperty"][2]["value"]
        self.description = component_dict["Properties"]["AbstractProperty"][3]["value"]
        self.image = component_dict["Properties"]["AbstractProperty"][4]["value"]

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend(
            [
                {
                    "@xsi:type": "ShortStringProperty",
                    "AllowEmpty": "false",
                    "ItemIdentifier": {"Id": self.id},
                    "propertyIdentifier": "Component_panel_formation_title_identifier",
                    "title": "Titre",
                    "value": self.titre,
                },
                {
                    "@xsi:type": "LongStringProperty",
                    "AllowEmpty": "false",
                    "ItemIdentifier": {"Id": self.id},
                    "propertyIdentifier": "Component_panel_formation_description_identifier",
                    "title": "Description",
                    "value": self.description,
                },
                {
                    "@xsi:type": "ImageProperty",
                    "ItemIdentifier": {"Id": self.id},
                    "propertyIdentifier": "Component_panel_formation_image_identifier",
                    "title": "Image",
                    "value": self.image,
                },
                {
                    "@xsi:type": "InteractiveProperty",
                    "ItemIdentifier": {"Id": self.id},
                    "propertyIdentifier": "Component_panel_formation_button_next_interactive_identifier",
                    "title": "Bouton suivant",
                    "value": {
                        "displayInProperties": "true",
                        "interactiveDirection": "Next",
                        "isActive": "true",
                    },
                },
                {
                    "@xsi:type": "InteractiveProperty",
                    "ItemIdentifier": {"Id": self.id},
                    "propertyIdentifier": "Component_panel_formation_button_previous_interactive_identifier",
                    "title": "Bouton précédent",
                    "value": {
                        "displayInProperties": "true",
                        "interactiveDirection": "Previous",
                        "isActive": "true",
                    },
                },
            ]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict

    def set_size(self, diameter_m):
        self.set_scale(
            diameter_m / self.base_width_m,
            diameter_m / self.base_width_m,
            diameter_m / self.base_width_m,
        )
        return self


components_object = [BoutonText, BoutonSimple, Texte, Timer, Zone, Panneau]


def parseComponent(components, links, component_id):
    if not isinstance(
        components["ArrayOfComponentMetadata"]["ComponentMetadata"], list
    ):
        components_data = [components["ArrayOfComponentMetadata"]["ComponentMetadata"]]
    else:
        components_data = components["ArrayOfComponentMetadata"]["ComponentMetadata"]
    component_ids = [c["ItemIdentifier"]["Id"] for c in components_data]

    try:
        comp_index = component_ids.index(component_id)
    except ValueError:
        return None
    comp_data = components_data[comp_index]
    new_component = Component(name="New Component")
    for cmp in components_object:
        if comp_data["NovComponentIdentifier"]["Id"] == cmp().nov_component_identifier:
            new_component = cmp(
                id=comp_data["ItemIdentifier"]["Id"],
                name=comp_data["Properties"]["AbstractProperty"][0]["value"],
                position=FullPosition(
                    position=PositionXYZ.model_validate(
                        comp_data["Properties"]["AbstractProperty"][1]["value"][
                            "position"
                        ]
                    ),
                    rotation=RotationXYZ.from_euler_angles(
                        PositionXYZ.model_validate(
                            comp_data["Properties"]["AbstractProperty"][1]["value"][
                                "rotation"
                            ]["eulerAngles"]
                        )
                    ),
                    scale=PositionXYZ.model_validate(
                        comp_data["Properties"]["AbstractProperty"][1]["value"]["scale"]
                    ),
                ),
            )
            break
    new_component.parse(comp_data)
    if "Link" in links["ArrayOfLink"].keys():
        if not isinstance(links["ArrayOfLink"]["Link"], list):
            link_data = [links["ArrayOfLink"]["ComponentMetadata"]]
        else:
            link_data = links["ArrayOfLink"]["Link"]
        links_comp_id = [
            link["ComponentMetadataIdentifier"]["Id"] for link in link_data
        ]
        print("Link ids ", links_comp_id)
        print("Comp id ", new_component.id)
        try:
            link_index = links_comp_id.index(new_component.id)
            new_component.target(link_data[link_index]["DestinationIdentifier"]["Id"])
        except ValueError:
            print("Not found")
            pass
    return new_component


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
    )
    id_anim = comp_data["Properties"]["AbstractProperty"][2]["value"][
        "animationIdentifier"
    ]["Id"]
    if id_anim:
        animation = Animation(id=id_anim)
    else:
        animation = Animation()

    new_component.animation = animation
    new_component.animation_status = comp_data["Properties"]["AbstractProperty"][2][
        "value"
    ]["playAnimationStatus"]
    new_component.set_path(dest_file)

    ## TODO : parse media animation
    # if(not isinstance(animations["ArrayOfFlowAnimation"]["Animation"], list)):
    #     link_data = [animations["ArrayOfLinkArrayOfFlowAnimation"]["ComponentMetadata"]]
    # else:
    #     link_data = animations["ArrayOfLink"]["Link"]
    # links_comp_id = [link["ComponentMetadataIdentifier"]["Id"] for link in link_data]
    # try:
    #     link_index = links_comp_id.index(new_component.id)
    # except ValueError:
    #     pass
    return new_component
