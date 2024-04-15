import copy
import shutil
from pathlib import Path

from .animation import Animation
from .tools import get_uuid, get_quaternion_from_euler


class Item:
    def __init__(self, name):
        self.id = get_uuid()
        self.name = name
        self.is_media = False
        self.is_active = True
        self.position = {"x": 0, "y": 0, "z": 0}
        self.rotation = {"x": 0, "y": 0, "z": 0}
        self.scale = {"x": 1, "y": 1, "z": 1}
        pass

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
                        "AllowEmpty": False
                    },
                    {
                        "@xsi:type": "TransformProperty",
                        "propertyIdentifier": "ItemPropertyTransformIdentifier",
                        "title": u"Position, rotation &amp; échelle",
                        "ItemIdentifier": {"Id": self.id},
                        "value":
                            {
                                "position": self.position,
                                "rotation":
                                    {
                                        **get_quaternion_from_euler(self.rotation),
                                        "eulerAngles": self.rotation
                                    },
                                "scale": self.scale
                            }
                    }]
            }
        }
        return item_dict

    def get_xml(self):
        return self.get_item_xml()

    def set_position(self, x=None, y=None, z=None):
        if x:
            self.position["x"] = x
        if y:
            self.position["y"] = y
        if z:
            self.position["z"] = z
        return self

    def set_rotation(self, x=None, y=None, z=None):
        if x:
            self.rotation["x"] = x
        if y:
            self.rotation["y"] = y
        if z:
            self.rotation["z"] = z
        return self

    def set_scale(self, x=None, y=None, z=None):
        if x:
            self.scale["x"] = x
        if y:
            self.scale["y"] = y
        if z:
            self.scale["z"] = z
        return self

    def clone(self):
        new_item = copy.copy(self)
        new_item.id = get_uuid()
        return new_item


class Component(Item):
    def __init__(self, name=""):
        super().__init__(name)
        self.property_identifier = ""
        self.nov_component_identifier = ""

    def parse(self, component_dict):
        pass

    def get_xml(self):
        component_dict = {
            "ItemIdentifier": {"Id": self.id},
            "IsActive": self.is_active,
            "Properties": {
                "AbstractProperty"
            }
        }


class BoutonText(Component):
    def __init__(self, name="Bouton texte", value="Click"):
        super().__init__(name)
        self.value = value
        self.property_identifier = "Component_button_text_interactive_identifier"
        self.to = None
        self.base_width_m = 0.15
        self.nov_component_identifier = "Component_button_text"

    def parse(self, component_dict):
        self.value = component_dict["Properties"]["AbstractProperty"][2]["value"]

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend([
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
                "value": {"displayInProperties": False, "interactiveDirection": "Next", "isActive": True},
            }]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict

    def target(self, dest_step):
        self.to = dest_step
        return self

    def set_size(self, diameter_m):
        self.set_scale(diameter_m / self.base_width_m, diameter_m / self.base_width_m, diameter_m / self.base_width_m)
        return self


class Media(Item):
    def __init__(self, path):
        super().__init__("media")
        self.is_media = True
        self.path = path
        self.animation = Animation()
        self.animation_status = "OnceAndClamp"

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend([
            {
                "@xsi:type": "AnimationProperty",
                "propertyIdentifier": "ItemPropertyAnimationIdentifier",
                "title": "Animation",
                "ItemIdentifier": {"Id": self.id},
                "value": {"animationIdentifier": self.animation.id},
                "playAnimationStatus": self.animation_status
            }]
        )
        item_dict["PathInDatabase"] = "Media/" + Path(self.path).name
        item_dict["InternalHierarchy"] = None
        return item_dict

    def set_width(self, width_m):
        self.set_scale(width_m, width_m, width_m)


class BoutonSimple(Component):
    def __init__(self, name="Bouton simple"):
        super().__init__(name)
        self.property_identifier = "Component_button_simple_interactive_identifier"
        self.to = None
        self.base_width_m = 0.15
        self.nov_component_identifier = "Component_button_simple"

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend([
            {
                "@xsi:type": "InteractiveProperty",
                "propertyIdentifier": self.property_identifier,
                "title": "Bouton suivant",
                "ItemIdentifier": {"Id": self.id},
                "value": {"displayInProperties": False, "interactiveDirection": "Next", "isActive": True},
            }]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict

    def target(self, dest_step):
        self.to = dest_step
        return self

    def set_size(self, diameter_m):
        self.set_scale(diameter_m / self.base_width_m, diameter_m / self.base_width_m, diameter_m / self.base_width_m)
        return self


class Timer(Component):
    def __init__(self, name="Timer", duration_s=1):
        super().__init__(name)
        self.property_identifier = "Component_timer_interactive_identifier"
        self.duration = duration_s
        self.to = None
        self.base_width_m = 0.15
        self.nov_component_identifier = "Component_timer"
    def parse(self, component_dict):
        self.duration = float(component_dict["Properties"]["AbstractProperty"][2]["value"])

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend([
            {
                "@xsi:type": "FloatProperty",
                "AllowEmpty": "false",
                "ItemIdentifier": {
                    "Id": self.id
                },
                "propertyIdentifier": "Component_timer_duration_identifier",
                "title": "Durée (en secondes)",
                "value": f"{self.duration}"
            },
            {
                "@xsi:type": "InteractiveProperty",
                "propertyIdentifier": self.property_identifier,
                "title": "Étape suivante",
                "ItemIdentifier": {"Id": self.id},
                "value": {"displayInProperties": False, "interactiveDirection": "Next", "isActive": True},
            }]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict

    def target(self, dest_step):
        self.to = dest_step
        return self

    def set_size(self, diameter_m):
        self.set_scale(diameter_m / self.base_width_m, diameter_m / self.base_width_m, diameter_m / self.base_width_m)
        return self


class Zone(Component):
    def __init__(self, name="Zone"):
        super().__init__(name)
        self.property_identifier = "Component_zone_interactive_identifier"
        self.to = None
        self.base_width_m = 0.15
        self.nov_component_identifier = "Component_zone"

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend([
            {
                "@xsi:type": "InteractiveProperty",
                "propertyIdentifier": self.property_identifier,
                "title": "Étape suivante",
                "ItemIdentifier": {"Id": self.id},
                "value": {"displayInProperties": False, "interactiveDirection": "Next", "isActive": True},
            }]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict

    def target(self, dest_step):
        self.to = dest_step
        return self

    def set_size(self, diameter_m):
        self.set_scale(diameter_m / self.base_width_m, diameter_m / self.base_width_m, diameter_m / self.base_width_m)
        return self

class Texte(Component):
    def __init__(self, name="Zone", value="Texte"):
        super().__init__(name)
        self.property_identifier = "Component_zone_interactive_identifier"
        self.value = value
        self.to = None
        self.base_width_m = 1
        self.nov_component_identifier = "Component_text"

    def parse(self, component_dict):
        self.value = component_dict["Properties"]["AbstractProperty"][2]["value"]

    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend([
            {
                "@xsi:type": "LongStringProperty",
                "AllowEmpty": "false",
                "ItemIdentifier": {
                    "Id": self.id
                },
                "propertyIdentifier": "Component_text_description_identifier",
                "title": "Texte",
                "value": self.value
            }]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict

    def target(self, dest_step):
        self.to = dest_step
        return self

    def set_size(self, diameter_m):
        self.set_scale(diameter_m / self.base_width_m, diameter_m / self.base_width_m, diameter_m / self.base_width_m)
        return self


class Panneau(Component):
    def __init__(self, name="Panneau", titre="Title", description="Description", image=None):
        super().__init__(name)
        self.property_identifier = "Component_panel_formation_button_next_interactive_identifier"
        self.titre = titre
        self.description = description
        self.image = image
        self.to = None
        self.base_width_m = 1
        self.nov_component_identifier = "Component_panel_formation"

    def parse(self, component_dict):
        self.titre = component_dict["Properties"]["AbstractProperty"][2]["value"]
        self.description =component_dict["Properties"]["AbstractProperty"][3]["value"]
        self.image = component_dict["Properties"]["AbstractProperty"][4]["value"]
    def get_xml(self):
        item_dict = self.get_item_xml()
        item_dict["Properties"]["AbstractProperty"].extend([
            {
                "@xsi:type": "ShortStringProperty",
                "AllowEmpty": "false",
                "ItemIdentifier": {
                    "Id": self.id
                },
                "propertyIdentifier": "Component_panel_formation_title_identifier",
                "title": "Titre",
                "value": self.titre
            },
            {
                "@xsi:type": "LongStringProperty",
                "AllowEmpty": "false",
                "ItemIdentifier": {
                    "Id": self.id
                },
                "propertyIdentifier": "Component_panel_formation_description_identifier",
                "title": "Description",
                "value": self.description
            },
            {
                "@xsi:type": "ImageProperty",
                "ItemIdentifier": {
                    "Id": self.id
                },
                "propertyIdentifier": "Component_panel_formation_image_identifier",
                "title": "Image",
                "value": self.image
            },
            {
                "@xsi:type": "InteractiveProperty",
                "ItemIdentifier": {
                    "Id": self.id
                },
                "propertyIdentifier": "Component_panel_formation_button_next_interactive_identifier",
                "title": "Bouton suivant",
                "value": {
                    "displayInProperties": "true",
                    "interactiveDirection": "Next",
                    "isActive": "true"
                }
            },
            {
                "@xsi:type": "InteractiveProperty",
                "ItemIdentifier": {
                    "Id": self.id
                },
                "propertyIdentifier": "Component_panel_formation_button_previous_interactive_identifier",
                "title": "Bouton précédent",
                "value": {
                    "displayInProperties": "true",
                    "interactiveDirection": "Previous",
                    "isActive": "true"
                }
            }]
        )
        item_dict["NovComponentIdentifier"] = {"Id": self.nov_component_identifier}
        return item_dict

    def target(self, dest_step):
        self.to = dest_step
        return self

    def set_size(self, diameter_m):
        self.set_scale(diameter_m / self.base_width_m, diameter_m / self.base_width_m, diameter_m / self.base_width_m)
        return self


components_object = [BoutonText, BoutonSimple, Texte, Timer, Zone, Panneau]
def parseComponent(components, links, component_id):
    if(not isinstance(components["ArrayOfComponentMetadata"]["ComponentMetadata"], list)):
        components_data = [components["ArrayOfComponentMetadata"]["ComponentMetadata"]]
    else:
        components_data = components["ArrayOfComponentMetadata"]["ComponentMetadata"]
    component_ids = [c["ItemIdentifier"]["Id"] for c in components_data]
    print(component_ids)
    print(component_id)
    try:
        comp_index = component_ids.index(component_id)
    except ValueError:
        return None
    comp_data = components_data[comp_index]
    new_component = Component()
    for cmp in components_object:
        if comp_data["NovComponentIdentifier"]["Id"] == cmp().nov_component_identifier:
            new_component = cmp()
            break
    new_component.id = comp_data["ItemIdentifier"]["Id"]
    new_component.name = comp_data["Properties"]["AbstractProperty"][0]["value"]
    new_component.position = comp_data["Properties"]["AbstractProperty"][1]["value"]["position"]
    new_component.rotation = comp_data["Properties"]["AbstractProperty"][1]["value"]["rotation"]["eulerAngles"]
    new_component.scale = comp_data["Properties"]["AbstractProperty"][1]["value"]["scale"]
    new_component.parse(comp_data)
    if "Link" in links["ArrayOfLink"].keys():
        if(not isinstance(links["ArrayOfLink"]["Link"], list)):
            link_data = [links["ArrayOfLink"]["ComponentMetadata"]]
        else:
            link_data = links["ArrayOfLink"]["Link"]
        links_comp_id = [link["ComponentMetadataIdentifier"]["Id"] for link in link_data]
        try:
            link_index = links_comp_id.index(new_component.id)
            new_component.target(link_data[link_index]["DestinationIdentifier"]["Id"])
        except ValueError:
            pass
    return new_component


def parseMedia(medias, animations, media_id, scenario_path, saving_media_path = Path.cwd().joinpath("temp")):
    if(not isinstance(medias["ArrayOfMediaMetadata"]["MediaMetadata"], list)):
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
    new_component = Media(dest_file)
    new_component.id = comp_data["ItemIdentifier"]["Id"]
    new_component.is_active = comp_data["IsActive"]
    new_component.name = comp_data["Properties"]["AbstractProperty"][0]["value"]
    new_component.position = comp_data["Properties"]["AbstractProperty"][1]["value"]["position"]
    new_component.rotation = comp_data["Properties"]["AbstractProperty"][1]["value"]["rotation"]["eulerAngles"]
    new_component.scale = comp_data["Properties"]["AbstractProperty"][1]["value"]["scale"]
    animation = Animation()
    animation.id = comp_data["Properties"]["AbstractProperty"][2]["value"]["animationIdentifier"]
    new_component.animation = animation
    new_component.animation_status = comp_data["Properties"]["AbstractProperty"][2]["playAnimationStatus"]
    new_component.path = dest_file
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



