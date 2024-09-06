import copy
import re
from pathlib import Path
from typing import List, TypedDict

from pydantic import BaseModel, Field
import xmltodict

from .media import Media

from .items import Item, Component
from .tools import get_uuid


class StepPos(BaseModel):
    x: float = 0
    y: float = 0


{
    "StepIdentifier": {"Id": "65a5acba"},
    "DisplayName": "Étape 02",
    "ComponentMetadataIdentifiers": [{"Id": "b14b53a1"}],
    "MediaMetadataIdentifiers": [],
},


class FlowStepPosDict(TypedDict):
    x: float
    y: float


class FlowIdDict(TypedDict):
    Id: str


class FlowStepDict(TypedDict):
    StepIdentifier: FlowIdDict
    DisplayName: str
    ComponentMetadataIdentifiers: list[FlowIdDict]
    MediaMetadataIdentifiers: list[FlowIdDict]


class FlowStepMetadataDict(TypedDict):
    StepIdentifier: FlowIdDict
    IsScenarioOrigin: bool
    LocalPositionInScenario: FlowStepPosDict


class Step(BaseModel):
    id: str = Field(default_factory=get_uuid)
    is_origin: bool = False
    items: List[Item | Media | Component] = Field(default_factory=list)
    name: str = "New Step"
    pos: StepPos = Field(default_factory=StepPos)

    def set_pos_grid(self, col, row):
        self.pos.x = col * 500 + 280
        self.pos.y = row * 400

    def get_xml(self):
        dict_metadata = {
            "StepMetadata": {
                "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "StepIdentifier": {"Id": self.id},
                "IsScenarioOrigin": self.is_origin,
                "LocalPositionInScenario": self.pos.model_dump(),
            }
        }
        component_dict = {
            "ComponentMetadataIdentifiers": None,
            "MediaMetadataIdentifiers": None,
        }
        for item in self.items:
            if item.is_media:
                if component_dict["MediaMetadataIdentifiers"] is None:
                    component_dict["MediaMetadataIdentifiers"] = {"ItemIdentifier": []}
                component_dict["MediaMetadataIdentifiers"]["ItemIdentifier"].append(
                    {"Id": item.id}
                )
                continue
            if component_dict["ComponentMetadataIdentifiers"] is None:
                component_dict["ComponentMetadataIdentifiers"] = {"ItemIdentifier": []}
            component_dict["ComponentMetadataIdentifiers"]["ItemIdentifier"].append(
                {"Id": item.id}
            )

        dict_step = {
            "Step": {
                "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "StepIdentifier": {"Id": self.id},
                "DisplayName": self.name,
                **component_dict.copy(),
            }
        }
        print(dict_step)
        return dict_step, dict_metadata

    def add(self, item, clone=False, item_name_prefix="", item_name_suffix=""):
        if hasattr(item, "components"):
            compo_n_item = []
            for component in item.components:
                if clone:
                    new_item = component.clone()
                    new_item.name = item_name_prefix + new_item.name + item_name_suffix
                    self.items.append(new_item)
                    compo_n_item.append(new_item)
                else:
                    self.items.append(component)
            if clone:
                new_item = copy.copy(item)
                new_item.set_components(compo_n_item)
                return new_item
            return item
        if clone:
            new_item = item.clone()
            new_item.name = item_name_prefix + new_item.name + item_name_suffix
            self.items.append(new_item)
        else:
            self.items.append(item)
        return item

    def add_placeholder(self, name="Placeholder"):
        return self.add(Media.get_placeholder(name))

    def save_step(self, scenario_path):
        print(scenario_path)
        step_path = Path(scenario_path).joinpath("Steps")
        step_path.mkdir(exist_ok=True)
        dict_step, dict_metadata = self.get_xml()
        step_file_path = step_path.joinpath(self.id + ".xml")
        step_metadata_file_path = step_path.joinpath(self.id + "_metadata.xml")
        with open(step_file_path, "w", encoding="utf-8") as fp:
            fp.write(
                xmltodict.unparse(dict_step, pretty=True, short_empty_elements=True)
            )
        with open(step_metadata_file_path, "w", encoding="utf-8") as fp:
            fp.write(
                xmltodict.unparse(dict_metadata, pretty=True, short_empty_elements=True)
            )

    def get_item_by_name(self, name):
        item_names = [item.name for item in self.items]
        try:
            item_index = item_names.index(name)
        except ValueError:
            return None
        return self.items[item_index]

    def get_item_by_id(self, id_item):
        item_ids = [item.id for item in self.items]
        try:
            item_index = item_ids.index(id_item)
        except ValueError:
            return None
        return self.items[item_index]

    def remove_item(self, matched_item):
        for item in self.items:
            if item == matched_item:
                self.items.remove(matched_item)
                return True
            return False

    def find_items_from_regex(self, name_regex: re.Pattern | str):
        if type(name_regex) is str:
            if not name_regex.endswith("$"):
                name_regex += "$"
            regex = re.compile(name_regex)
        elif type(name_regex) is re.Pattern:
            regex = name_regex
        else:
            return None
        found_items = []
        for item in self.items:
            if regex.match(item.name):
                found_items.append(item)
        return found_items

    def remove_items_from_regex(self, name_regex: re.Pattern | str):
        for item in self.find_items_from_regex(name_regex):
            self.remove_item(item)

    def merge_step(self, step, clone=False):
        for item in step.items:
            self.add(item, clone, item_name_prefix=self.name + "_")

    def clone(self):
        new_step = copy.copy(self)
        item_ids = {}
        new_items = []
        for item in self.items:
            item_clone = item.clone()
            new_items.append(item_clone)
            item_ids[item.id] = item_clone.id
        new_step.id = get_uuid()
        return new_step

    def set_metadata(self, metadata: FlowStepMetadataDict):
        self.pos.x = metadata["LocalPositionInScenario"]["x"]
        self.pos.y = metadata["LocalPositionInScenario"]["x"]
        self.is_origin = metadata["IsScenarioOrigin"]

    @staticmethod
    def parse(step_dict: FlowStepDict, metadata: FlowStepMetadataDict = None):
        ##TODO how to parse for components ?
        step = Step(id=step_dict["StepIdentifier"]["Id"], name=step_dict["DisplayName"])
        step.set_metadata(metadata=metadata)
        return step
