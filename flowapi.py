import copy
import datetime
import math
import shutil
import uuid
from pathlib import Path
from typing import List

import xmltodict

uuid_list = [0]
global_scenario_path = Path("Scenarios")


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
    roll = eulerAngles["x"] * math.pi / 180
    pitch = eulerAngles["y"] * math.pi / 180
    yaw = eulerAngles["z"] * math.pi / 180
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
    new_uuid = uuid_list[-1]+1
    uuid_list.append(new_uuid)
    return f'{new_uuid:08x}'


class Animation:
    def __init__(self):
        self.id = get_uuid()
        self.media_path = ""
        self.name = ""
        self.duration = 0
        self.transformations = {
            "position":
                {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
            "rotation":
                {
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "w": 1,
                    "eulerAngles":
                        {
                            "x": 0,
                            "y": 0,
                            "z": 0
                        }
                },
            "scale":
                {
                    "x": 1,
                    "y": 1,
                    "z": 1
                }
        }

    def get_dict(self):
        animation_dict = {
            "FlowAnimation":
                {
                    "AnimationIdentifier":
                        {"Id": self.id
                         },
                    "DisplayName": self.name,
                    "Duration": self.duration,
                    "Transformations": {
                        "ValueTupleOfStringHFTransform":
                            {
                                "Item1": None,
                                "Item2": self.transformations
                            }
                    }
                },

        }
        return animation_dict


class Scenario:
    def __init__(self, name="Scenario", id = None):
        self.id = get_uuid() if id is None else id
        self.pos = {"x": 0, "y": 0}
        self.name = name
        self.description = ""
        self.is_origin = False
        self.steps: List[Step] = []
        self.items: List[Media | Component] = []
        self.links: List[Link] = []
        self.animations: List[Animation] = []
        self.last_date_save = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=1)))

    def add_step(self, step):
        if len(self.steps) == 0:
            step.is_origin = True
        step.pos["x"] = len(self.steps) * 400 + 400
        self.steps.append(step)
        return step

    def get_config_xml(self):
        step_identifiers = None
        for step in self.steps:
            if step_identifiers is None:
                step_identifiers = []
            step_identifiers.append({

                "Id": step.id
            })
        link_identifiers = None
        for link in self.links:
            if link_identifiers is None:
                link_identifiers = []
            link_identifiers.append({
                "Id": link.id
            })
        config_dict = {
            "Scenario":
                {
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "ScenarioIdentifier":
                        {
                            "Id": self.id
                        },
                    "DisplayName": self.name,
                    "Description": self.description,
                    "LastSaveDateName": self.last_date_save.isoformat(),
                    "StepIdentifiers": {"StepIdentifier": step_identifiers},
                    "LinkIdentifiers": ({"LinkIdentifier": link_identifiers} if link_identifiers is not None else None),
                }
        }
        return config_dict

    def get_animation_xml(self):
        self.animations = []
        for item in self.items:
            if item.is_media:
                self.animations.append(item.animation)

        animation_dict = {
            "ArrayOfFlowAnimation":
                {
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                }
        }
        animations = [animation.get_dict() for animation in self.animations]
        if len(animations) > 0:
            animation_dict["ArrayOfFlowAnimation"]["FlowAnimation"] = [animation["FlowAnimation"] for animation in
                                                                       animations]
        return animation_dict

    def get_scenario_metadata_xml(self):
        scenario_metadata = {
            "ScenarioMetadata":
                {
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "ScenarioIdentifier":
                        {"Id": self.id},
                    "Pivot": {
                        "position":
                            {
                                "x": 0,
                                "y": 0,
                                "z": 0
                            },
                        "rotation":
                            {
                                "x": 0,
                                "y": 0,
                                "z": 0,
                                "w": 1,
                                "eulerAngles":
                                    {
                                        "x": 0,
                                        "y": 0,
                                        "z": 0
                                    }
                            },
                        "scale":
                            {
                                "x": 1,
                                "y": 1,
                                "z": 1
                            }
                    },
                    "LastCanvasTransform": {
                        "position":
                            {
                                "x": 0,
                                "y": 0,
                                "z": 0
                            },
                        "rotation":
                            {
                                "x": 0,
                                "y": 0,
                                "z": 0,
                                "w": 1,
                                "eulerAngles":
                                    {
                                        "x": 0,
                                        "y": 0,
                                        "z": 0
                                    }
                            },
                        "scale":
                            {
                                "x": 1,
                                "y": 1,
                                "z": 1
                            }
                    }
                }
        }
        return scenario_metadata

    def get_links_xml(self):
        self.links = []
        for step in self.steps:
            for item in step.items:
                if not item.is_media:
                    if hasattr(item, "to"):
                        if item.to is not None:
                            if (step != item.to):
                                link = Link(step, item.to, item)
                                self.links.append(link)

        links_content_xml = [link.get_xml() for link in self.links]
        links_xml = {
            "ArrayOfLink":
                {
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                }
        }
        if (len(links_content_xml)) > 0:
            links_xml["ArrayOfLink"]["Link"] = links_content_xml
        return links_xml

    @property
    def components(self):
        items = []
        for step in self.steps:
            for item in step.items:
                if not item.is_media:
                    items.append(item)
        return items

    def get_components_xml(self):
        items = []
        for step in self.steps:
            for item in step.items:
                print(item)
                if not item.is_media:
                    items.append(item)
        component_dict = {
            "ArrayOfComponentMetadata":
                {
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "ComponentMetadata": [item.get_xml() for item in items]
                }
        }
        return component_dict

    def get_medias_xml(self):
        media_dir = global_scenario_path.joinpath(self.id).joinpath("Media")
        media_dir.mkdir(exist_ok=True)
        items = []
        for step in self.steps:
            for item in step.items:
                if item.is_media:
                    shutil.copyfile(Path(item.path), media_dir.joinpath(Path(item.path).name))
                    items.append(item)
        metadata_xml = [item.get_xml() for item in items]
        component_dict = {
            "ArrayOfMediaMetadata":
                {
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                }
        }
        if len(metadata_xml) > 0:
            component_dict["ArrayOfMediaMetadata"]["MediaMetadata"] = metadata_xml
        return component_dict

    def save_scenario(self):
        scenario_path = global_scenario_path.joinpath(self.id)
        scenario_path.mkdir(exist_ok=True)

        animation_file = scenario_path.joinpath("animations.xml")
        with open(animation_file, "w", encoding='utf-8') as fp:
            fp.write(xmltodict.unparse(self.get_animation_xml(), pretty=True, short_empty_elements=True))

        scenario_metadata_file = scenario_path.joinpath("scenario_metadata.xml")
        with open(scenario_metadata_file, "w", encoding='utf-8') as fp:
            fp.write(xmltodict.unparse(self.get_scenario_metadata_xml(), pretty=True, short_empty_elements=True))

        links_file = scenario_path.joinpath("links.xml")
        with open(links_file, "w", encoding='utf-8') as fp:
            fp.write(xmltodict.unparse(self.get_links_xml(), pretty=True, short_empty_elements=True))

        component_file = scenario_path.joinpath("component_metadatas.xml")
        with open(component_file, "w", encoding='utf-8') as fp:
            fp.write(xmltodict.unparse(self.get_components_xml(), pretty=True, short_empty_elements=True))

        media_file = scenario_path.joinpath("media_metadatas.xml")
        with open(media_file, "w", encoding='utf-8') as fp:
            fp.write(xmltodict.unparse(self.get_medias_xml(), pretty=True, short_empty_elements=True))

        config_file = scenario_path.joinpath("config.xml")
        with open(config_file, "w", encoding='utf-8') as fp:
            fp.write(xmltodict.unparse(self.get_config_xml(), pretty=True, short_empty_elements=True))

        for step in self.steps:
            step.save_step(scenario_path)


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
        item_dict["NovComponentIdentifier"] = {"Id": "Component_button_text"}
        return item_dict

    def target(self, dest_step):
        self.to = dest_step
        return self

    def set_size(self, diameter_m):
        self.set_scale(diameter_m/self.base_width_m, diameter_m/self.base_width_m, diameter_m/self.base_width_m)


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


class Step:
    def __init__(self, name="New step", origin=False):
        self.id = get_uuid()
        self.is_origin = origin
        self.items: List[Item] = []
        self.name = name
        self.pos = {"x": 0, "y": 0}

    def get_xml(self):
        dict_metadata = \
            {"StepMetadata":
                {
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "StepIdentifier":
                        {"Id": self.id},
                    "IsScenarioOrigin": self.is_origin,
                    "LocalPositionInScenario":
                        {
                            "x": self.pos["x"],
                            "y": self.pos["y"],
                        }
                }
            }
        component_dict = {
            "ComponentMetadataIdentifiers": None,
            "MediaMetadataIdentifiers": None
        }
        for item in self.items:
            if item.is_media:
                if component_dict["MediaMetadataIdentifiers"] is None:
                    component_dict["MediaMetadataIdentifiers"] = {"ItemIdentifier": []}
                component_dict["MediaMetadataIdentifiers"]["ItemIdentifier"].append({"Id": item.id})
            if component_dict["ComponentMetadataIdentifiers"] is None:
                component_dict["ComponentMetadataIdentifiers"] = {"ItemIdentifier": []}
            component_dict["ComponentMetadataIdentifiers"]["ItemIdentifier"].append({"Id": item.id})

        dict_step = \
            {"Step":
                {
                    "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "StepIdentifier":
                        {"Id": self.id},
                    "DisplayName": self.name,
                    **component_dict.copy()
                }
            }
        print(dict_step)
        return dict_step, dict_metadata

    def add(self, item: Item, clone=False):
        if (hasattr(item, "components")):
            for component in item.components:
                if clone:
                    self.items.append(component.clone())
                else:
                    self.items.append(component)
            return item
        if clone:
            self.items.append(item.clone())
        else:
            self.items.append(item)
        return item

    def save_step(self, scenario_path):
        print(scenario_path)
        step_path = Path(scenario_path).joinpath("Steps")
        step_path.mkdir(exist_ok=True)
        dict_step, dict_metadata = self.get_xml()
        step_file_path = step_path.joinpath(self.id + ".xml")
        step_metadata_file_path = step_path.joinpath(self.id + "_metadata.xml")
        with open(step_file_path, "w", encoding='utf-8') as fp:
            fp.write(xmltodict.unparse(dict_step, pretty=True, short_empty_elements=True))
        with open(step_metadata_file_path, "w", encoding='utf-8') as fp:
            fp.write(xmltodict.unparse(dict_metadata, pretty=True, short_empty_elements=True))


class Link:
    def __init__(self, from_step, dest_step, source_component):
        self.id = get_uuid()
        self.from_step: Step = from_step
        self.dest_step: Step = dest_step
        self.source_component: Component = source_component

    def get_xml(self):
        link_dict = {
            "LinkIdentifier": {"Id": self.id},
            "StepIdentifier": {"Id": self.from_step.id},
            "ComponentMetadataIdentifier": {"Id": self.source_component.id},
            "PropertyIdentifier": {"Id": self.source_component.property_identifier},
            "DestinationIdentifier": {"Id": self.dest_step.id},
        }
        return link_dict


class LinearComponentArray:
    def __init__(self, number_per_column, row_pitch, col_pitch):
        self.components = []
        self.number_per_column = number_per_column
        self.position = {"x": 0, "y": 0, "z": 0}
        self.col_pitch = col_pitch
        self.row_pitch = row_pitch

    def update_component_positions(self):
        for i in range(len(self.components)):
            row_i = i // self.number_per_column
            position = self.position.copy()
            position["x"] += (i % self.number_per_column) * self.col_pitch
            position["y"] += row_i * self.row_pitch
            self.components[i].set_position(**position)

    def set_components(self, components):
        self.components = components
        self.update_component_positions()

class CircularComponentArray:
    def __init__(self, diameter):
        self.components = []
        self.position = {"x": 0, "y": 0, "z": 0}
        self.diameter = diameter


    def update_component_positions(self):
        for i in range(len(self.components)):
            x_offset = self.diameter*math.sin()
            row_i = i // self.number_per_column
            position = self.position.copy()
            position["x"] += (i % self.number_per_column) * self.col_pitch
            position["y"] += row_i * self.row_pitch
            self.components[i].set_position(**position)

    def set_components(self, components, clone=False):
        if clone:
            self.components = [component.clone() for component in components]
        else:
            self.components = components
        self.update_component_positions()

class ComponentGroup:
    def __init__(self):
        self.position = {"x": 0, "y": 0, "z": 0}
        self.rotation = {"x": 0, "y": 0, "z": 0}
        self.scale = {"x": 1, "y": 1, "z": 1}
        self.components = []
        self.relative_component_position = []

    def add_component(self, component, relative_position=None, clone = False):
        if relative_position is None:
            relative_position = {"x": 0, "y": 0, "z": 0}
        self.components.append(component.clone() if clone else component)
        self.relative_component_position.append(relative_position.copy())
        self.update_component_position()

    def update_component_position(self):
        for component in self.components:
            relative_pos = self.relative_component_position[self.components.index(component)]
            comp_pos = {
                "x":self.position["x"]+relative_pos["x"],
                "y":self.position["y"]+relative_pos["y"],
                "z":self.position["z"]+relative_pos["z"],
            }
            component.set_position(x=comp_pos["x"], y= comp_pos["y"], z=comp_pos["z"])

    def set_position(self,x=None, y=None, z=None):
        if x:
            self.position["x"] = x
        if y:
            self.position["y"] = y
        if z:
            self.position["z"] = z
        self.update_component_position()
        return self

from cairosvg import svg2png
def generate_odm_pane(text, image_id=None):
    uuid_image = str(uuid.uuid4()) if image_id is None else image_id
    with open("odm.svg","r",encoding="utf-8") as f:
        image_svg = f.read()
    image_svg=image_svg.replace("$ODM", text)
    svg2png(image_svg.encode(encoding="utf-8"),write_to=uuid_image+'.png')
    return Path(uuid_image+'.png')

class PanneauBouton(ComponentGroup):
    def __init__(self, title_panneau):
        super().__init__()
        self.panneau_image_path = generate_odm_pane(title_panneau)
        self.panneau_image = Media(self.panneau_image_path)
        self.bouton_1 = BoutonText("->","1")
        self.bouton_2 = BoutonText("X","2")
        self.bouton_3 = BoutonText("C","3")
        self.bouton_4 = BoutonText("4","4")
        self.add_component(self.panneau_image)
        self.add_component(self.bouton_1, relative_position={"x":0.3, "y":0.15, "z":-0.05})
        self.add_component(self.bouton_2, relative_position={"x":0.3, "y":0.013, "z":-0.05})
        self.add_component(self.bouton_3, relative_position={"x":0.3, "y":-0.125, "z":-0.05})
        self.add_component(self.bouton_4, relative_position={"x":0.3, "y":-0.27, "z":-0.05})

class Dialog(Media):
    def __init__(self, color = "#FF0000", message="Dialog"):
        uuid_image = str(uuid.uuid4())
        with open("dialog.svg", "r", encoding="utf-8") as f:
            image_svg = f.read()
        image_svg = image_svg.replace("$Message", message).replace("#000000", color)
        svg2png(image_svg.encode(encoding="utf-8"), write_to=uuid_image + '.png')
        super().__init__(Path(uuid_image + '.png'))
        self.set_width(2)

new_scenario = Scenario("1000 Buttons scenario", id="00000004")
# On ajoute les étapes
steps = [] # La liste de toutes les étapes pour pouvoir y acceder et les modifier ensuite
for i in range(100):
    steps.append(new_scenario.add_step(Step(f"etape_{i}")))
# On crée une grille de 10 boutons, chaque bouton a une étape en target
boutons = []
for i in range(100):
    boutons.append(BoutonText(value=f"Bouton {i}").target(steps[i]))
# On arrange ces boutons selon une grille de 5 colonne avec un pitch entre les ligne de 0.2m idem entre les colonnes
bouton_array = LinearComponentArray(5, 0.2, 0.2)
bouton_array.set_components(boutons) # On ajoute les boutons à la matrice de componsants

# A chaque étape on ajoute la grille de bouton. Il faut cloner la grille car on ne peut pas utiliser
# le meme bouton deux fois dans le scénario (même dans des étapes differentes)
# steps[0].add(PanneauBouton("Panneau 1").set_position(x=0))
# steps[0].add(PanneauBouton("Panneau 2").set_position(x=1))
# steps[0].add(PanneauBouton("Panneau 3").set_position(x=2))
# steps[0].add(Dialog("#FF0000", "ATTENTION GROS GROS PROBLEME").set_position(y=1))
# steps[0].add(Dialog("#FF9955", "ATTENTION MOYEN PROBLEME").set_position(x=2,y=1))
# steps[0].add(Dialog("#3771C8", "JUSTE UNE INFO COMME CA").set_position(x=4,y=1))
for i,step in enumerate(steps):
    step.add(bouton_array, clone=True)
# On enregistre le scénario
new_scenario.save_scenario()
