import copy
import datetime
from html.entities import name2codepoint
import re
import shutil
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field
import xmltodict

from .media import Media, VideoMedia, parseMedia, AudioMedia

from .step import Step
from .items import Component, parseComponent, BoutonImage
from .link import Link
from .animation import Animation
from .tools import get_uuid, global_scenario_path, uuid_list


class ScenarioPos(BaseModel):
    x: float = 0
    y: float = 0


class Scenario(BaseModel):
    id: str = Field(default_factory=get_uuid)
    pos: ScenarioPos = Field(default_factory=ScenarioPos)
    step_by_row: int = 5
    name: str = "Scénario"
    description: str = ""
    steps: List[Step] = []
    links: List[Link] = []
    animations: List[Animation] = []
    last_date_save: datetime.datetime = datetime.datetime.now(
        tz=datetime.timezone(datetime.timedelta(hours=1))
    )

    def add_step(self, step, auto_pos=True):
        if len(self.steps) == 0:
            step.is_origin = True
        if auto_pos:
            step.pos.x = (len(self.steps) % self.step_by_row) * 400 + 280
            step.pos.y = 1050 - (len(self.steps) // self.step_by_row) * 400
        self.steps.append(step)
        return step

    def get_config_xml(self):
        step_identifiers = None
        for step in self.steps:
            if step_identifiers is None:
                step_identifiers = []
            step_identifiers.append({"Id": step.id})
        link_identifiers = None
        for link in self.links:
            if link_identifiers is None:
                link_identifiers = []
            link_identifiers.append({"Id": link.id})
        config_dict = {
            "Scenario": {
                "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "ScenarioIdentifier": {"Id": self.id},
                "DisplayName": self.name,
                "Description": self.description,
                "LastSaveDateTime": self.last_date_save.isoformat(),
                "StepIdentifiers": {"StepIdentifier": step_identifiers},
                "LinkIdentifiers": (
                    {"LinkIdentifier": link_identifiers}
                    if link_identifiers is not None
                    else None
                ),
            }
        }
        return config_dict

    def get_animation_xml(self):
        self.animations = []
        anim_ids = []
        for step in self.steps:
            for item in step.items:
                if isinstance(item, (AudioMedia, Media, VideoMedia)):
                    if item.animation.id not in anim_ids:
                        self.animations.append(item.animation)
                        anim_ids.append(item.animation.id)

        animation_dict = {
            "ArrayOfFlowAnimation": {
                "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            }
        }
        animations = [animation.get_dict() for animation in self.animations]
        if len(animations) > 0:
            animation_dict["ArrayOfFlowAnimation"]["FlowAnimation"] = [
                animation["FlowAnimation"] for animation in animations
            ]
        return animation_dict

    def get_scenario_metadata_xml(self):
        scenario_metadata = {
            "ScenarioMetadata": {
                "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "ScenarioIdentifier": {"Id": self.id},
                "Pivot": {
                    "position": {"x": 0, "y": 0, "z": 0},
                    "rotation": {
                        "x": 0,
                        "y": 0,
                        "z": 0,
                        "w": 1,
                        "eulerAngles": {"x": 0, "y": 0, "z": 0},
                    },
                    "scale": {"x": 1, "y": 1, "z": 1},
                },
                "LastCanvasTransform": {
                    "position": {"x": 0, "y": 0, "z": 0},
                    "rotation": {
                        "x": 0,
                        "y": 0,
                        "z": 0,
                        "w": 1,
                        "eulerAngles": {"x": 0, "y": 0, "z": 0},
                    },
                    "scale": {"x": 1, "y": 1, "z": 1},
                },
            }
        }
        return scenario_metadata

    def get_links_xml(self):
        self.links = []
        for step in self.steps:
            for item in step.items:
                if isinstance(item, Component):
                    if hasattr(item, "to"):
                        if item.to is not None:
                            if step.id != item.to:
                                target_step = self.get_step_by_id(item.to)
                                if target_step is not None:
                                    link = Link(
                                        from_step=step,
                                        dest_step=target_step,
                                        source_component=item,
                                    )
                                    self.links.append(link)

        links_content_xml = [link.get_xml() for link in self.links]
        links_xml = {
            "ArrayOfLink": {
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

    def get_components_xml(self, output_folder):
        items = []
        icon_dir = Path(output_folder).joinpath(self.id).joinpath("Steps/Extras")
        for step in self.steps:
            for item in step.items:
                if not item.is_media:
                    items.append(item)
                    if isinstance(item, BoutonImage):
                        icon_dir.mkdir(exist_ok=True, parents=True)
                        shutil.copyfile(
                            Path(item.path),
                            icon_dir.joinpath(item.get_target_image_name()),
                        )

        component_dict = {
            "ArrayOfComponentMetadata": {
                "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "ComponentMetadata": [item.get_xml() for item in items],
            }
        }
        return component_dict

    def get_medias_xml(self, output_folder=global_scenario_path):
        media_dir = output_folder.joinpath(self.id).joinpath("Media")
        media_dir.mkdir(exist_ok=True)
        items = []
        for step in self.steps:
            for item in step.items:
                if type(item) in [Media, AudioMedia, VideoMedia]:
                    if not item.internal_media:
                        shutil.copyfile(
                            Path(item.path),
                            media_dir.joinpath(item.id + Path(item.path).suffix),
                        )
                    items.append(item)
        metadata_xml = [item.get_xml() for item in items]
        component_dict = {
            "ArrayOfMediaMetadata": {
                "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            }
        }
        if len(metadata_xml) > 0:
            component_dict["ArrayOfMediaMetadata"]["MediaMetadata"] = metadata_xml
        return component_dict

    def save_scenario(self, output_folder=global_scenario_path):
        scenario_path = output_folder.joinpath(self.id)
        scenario_path.mkdir(exist_ok=True)

        animation_file = scenario_path.joinpath("animations.xml")
        with open(animation_file, "w", encoding="utf-8") as fp:
            fp.write(
                xmltodict.unparse(
                    self.get_animation_xml(), pretty=True, short_empty_elements=True
                )
            )

        scenario_metadata_file = scenario_path.joinpath("scenario_metadata.xml")
        with open(scenario_metadata_file, "w", encoding="utf-8") as fp:
            fp.write(
                xmltodict.unparse(
                    self.get_scenario_metadata_xml(),
                    pretty=True,
                    short_empty_elements=True,
                )
            )

        links_file = scenario_path.joinpath("links.xml")
        with open(links_file, "w", encoding="utf-8") as fp:
            fp.write(
                xmltodict.unparse(
                    self.get_links_xml(), pretty=True, short_empty_elements=True
                )
            )

        component_file = scenario_path.joinpath("component_metadatas.xml")
        with open(component_file, "w", encoding="utf-8") as fp:
            fp.write(
                xmltodict.unparse(
                    self.get_components_xml(output_folder),
                    pretty=True,
                    short_empty_elements=True,
                )
            )

        media_file = scenario_path.joinpath("media_metadatas.xml")
        with open(media_file, "w", encoding="utf-8") as fp:
            fp.write(
                xmltodict.unparse(
                    self.get_medias_xml(output_folder),
                    pretty=True,
                    short_empty_elements=True,
                )
            )

        config_file = scenario_path.joinpath("config.xml")
        with open(config_file, "w", encoding="utf-8") as fp:
            fp.write(
                xmltodict.unparse(
                    self.get_config_xml(), pretty=True, short_empty_elements=True
                )
            )

        for step in self.steps:
            step.save_step(scenario_path)
        return scenario_path

    def get_step_by_name(self, name):
        step_names = [step.name for step in self.steps]
        try:
            step_index = step_names.index(name)
        except ValueError:
            return None
        return self.steps[step_index]

    def get_step_by_id(self, id):
        step_names = [step.id for step in self.steps]
        try:
            step_index = step_names.index(id)
        except ValueError:
            return None
        return self.steps[step_index]

    def add_scenario_to_step(self, current_step, scenario):
        step_to_replace = self.steps.pop(self.steps.index(current_step))
        scenario_clone = scenario.clone()
        for step in scenario_clone:
            new_step = step_to_replace.clone()
            step.merge_step(new_step, clone=True)
            self.add_step(step)

    def find_item_by_id(self, id):
        for step in self.steps:
            for item in step.items:
                if item.id == id:
                    return item
        return None

    def remove_item(self, item):
        for step in self.steps:
            step.remove_item(item)

    def find_steps_from_regex(self, name_regex: re.Pattern | str):
        if type(name_regex) is str:
            if not name_regex.endswith("$"):  # Adds $ to match end of string
                name_regex += "$"
            regex = re.compile(name_regex)
        elif type(name_regex) is re.Pattern:
            regex = name_regex
        else:
            return None
        found_steps = []
        for step in self.steps:
            if regex.match(step.name):
                found_steps.append(step)
        return found_steps

    def find_items_by_path(self, path):
        """
        path is regex_step/regex_item or regex_item
        :param path:
        :return: matched items
        """
        split_path = path.split("/")
        if len(split_path) == 1:
            matched_steps = self.steps
            item_regex = split_path[0]
        else:
            step_regex = split_path[0]
            item_regex = split_path[1]
            step_regex = ".*" if step_regex == "*" else step_regex
            matched_steps = self.find_steps_from_regex(step_regex)
        item_regex = ".*" if item_regex == "*" else item_regex

        if not matched_steps:
            return []
        matched_items = []
        for step in matched_steps:
            found_items = step.find_items_from_regex(item_regex)
            matched_items.extend(found_items if found_items else [])
        return matched_items

    def clone(self):
        step_ids: dict[str, str] = {}
        new_steps = []
        for step in self.steps:
            step_clone = step.clone()
            new_steps.append(step_clone)
            step_ids[step.id] = step_clone.id
        new_scenario = copy.copy(self)
        new_scenario.id = get_uuid()
        new_scenario.steps = new_steps
        for step in new_scenario.steps:
            for item in step.items:
                if isinstance(item, Component):
                    if item.to:
                        item.to = new_scenario.get_step_by_id(step_ids[item.to]).id
        return new_scenario

    @staticmethod
    def parse(scenario_path: Path):
        config_file = scenario_path.joinpath("config.xml")
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = xmltodict.parse(f.read())
        uuids = []
        uuids.extend([])
        animation_file = scenario_path.joinpath("animations.xml")
        with open(animation_file, "r", encoding="utf-8") as f:
            animation_data = xmltodict.parse(f.read())
        component_file = scenario_path.joinpath("component_metadatas.xml")
        with open(component_file, "r", encoding="utf-8") as f:
            component_data = xmltodict.parse(f.read())

        link_file = scenario_path.joinpath("links.xml")
        with open(link_file, "r", encoding="utf-8") as f:
            links_data = xmltodict.parse(f.read())
        media_file = scenario_path.joinpath("media_metadatas.xml")
        with open(media_file, "r", encoding="utf-8") as f:
            media_data = xmltodict.parse(f.read())
        scenario_file = scenario_path.joinpath("scenario_metadata.xml")
        scenario = Scenario()
        scenario.name = config_data["Scenario"]["DisplayName"]
        scenario.id = config_data["Scenario"]["ScenarioIdentifier"]["Id"]
        uuids.append(scenario.id)
        scenario.description = config_data["Scenario"]["Description"]
        # scenario.last_date_save = datetime.datetime.fromisoformat(config_data["Scenario"]["LastSaveDateTime"])
        if isinstance(
            config_data["Scenario"]["StepIdentifiers"]["StepIdentifier"], list
        ):
            steps_id = [
                step["Id"]
                for step in config_data["Scenario"]["StepIdentifiers"]["StepIdentifier"]
            ]
        else:
            steps_id = [
                config_data["Scenario"]["StepIdentifiers"]["StepIdentifier"]["Id"]
            ]
        uuids.extend(steps_id)
        for step in steps_id:
            with open(
                scenario_path.joinpath("Steps").joinpath(step + ".xml"),
                "r",
                encoding="utf-8",
            ) as f:
                step_info = xmltodict.parse(f.read())
            with open(
                scenario_path.joinpath("Steps").joinpath(step + "_metadata.xml"),
                "r",
                encoding="utf-8",
            ) as f:
                step_metadata = xmltodict.parse(f.read())
            step_obj = Step(name=step_info["Step"]["DisplayName"])
            step_obj.id = step_info["Step"]["StepIdentifier"]["Id"]
            step_obj.pos = step_metadata["StepMetadata"]["LocalPositionInScenario"]
            step_obj.is_origin = step_metadata["StepMetadata"]["IsScenarioOrigin"]
            if step_info["Step"]["ComponentMetadataIdentifiers"] is None:
                comp_id = []
            else:
                if isinstance(
                    step_info["Step"]["ComponentMetadataIdentifiers"]["ItemIdentifier"],
                    list,
                ):
                    comp_id = [
                        component["Id"]
                        for component in step_info["Step"][
                            "ComponentMetadataIdentifiers"
                        ]["ItemIdentifier"]
                    ]
                else:
                    comp_id = [
                        step_info["Step"]["ComponentMetadataIdentifiers"][
                            "ItemIdentifier"
                        ]["Id"]
                    ]
            for component in comp_id:
                new_component = parseComponent(
                    component_data, links_data, component, scenario_path
                )
                if new_component is not None:
                    uuids.append(new_component.id)
                    step_obj.add(new_component)
            if step_info["Step"]["MediaMetadataIdentifiers"] is None:
                media_ids = []
            else:
                if isinstance(
                    step_info["Step"]["MediaMetadataIdentifiers"]["ItemIdentifier"],
                    list,
                ):
                    media_ids = [
                        media["Id"]
                        for media in step_info["Step"]["MediaMetadataIdentifiers"][
                            "ItemIdentifier"
                        ]
                    ]
                else:
                    media_ids = [
                        step_info["Step"]["MediaMetadataIdentifiers"]["ItemIdentifier"][
                            "Id"
                        ]
                    ]
            for media in media_ids:
                new_component = parseMedia(
                    media_data, animation_data, media, scenario_path
                )
                uuids.append(new_component.id)
                step_obj.add(new_component)
            scenario.add_step(step_obj)
        step_ids = [st.id for st in scenario.steps]
        for step in scenario.steps:
            for comp in step.items:
                if hasattr(comp, "to"):
                    if comp.to is not None:
                        comp.to = scenario.steps[step_ids.index(comp.to)].id
        uuid_list.extend(uuids)
        return scenario
