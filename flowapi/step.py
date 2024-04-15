import copy
import re
from pathlib import Path
from typing import List

import xmltodict

from .items import Item, Media, Component
from .tools import get_uuid


class Step:
    def __init__(self, name="New step", origin=False):
        self.id = get_uuid()
        self.is_origin = origin
        self.items: List[Item | Media | Component] = []
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

    def add(self, item: Item, clone=False, item_name_prefix='', item_name_suffix=''):
        if (hasattr(item, "components")):
            for component in item.components:
                if clone:
                    new_item = component.clone()
                    new_item.name = item_name_prefix + new_item.name + item_name_suffix
                    self.items.append(new_item)
                else:
                    self.items.append(component)
            return item
        if clone:
            new_item = item.clone()
            new_item.name = item_name_prefix + new_item.name + item_name_suffix
            self.items.append(new_item)
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
