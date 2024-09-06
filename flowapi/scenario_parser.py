from pathlib import Path

import xmltodict

from flowapi.media import parseMedia
from flowapi.step import StepPos
import flowapi.tools
from flowapi import Scenario, Step
from flowapi.items import parseComponent
import json

def parseScenario(scenario_path: Path):
    config_file = scenario_path.joinpath("config.xml")
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = xmltodict.parse(f.read())
    print(config_data)
    uuids = []
    uuids.extend([])
    animation_file = scenario_path.joinpath("animations.xml")
    with open(animation_file, "r", encoding="utf-8") as f:
        animation_data = xmltodict.parse(f.read())
    json.dump(animation_data,open("animation_json.json","w"))
    
    component_file = scenario_path.joinpath("component_metadatas.xml")
    with open(component_file, "r", encoding="utf-8") as f:
        component_data = xmltodict.parse(f.read())
    print(component_data)

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
    if isinstance(config_data["Scenario"]["StepIdentifiers"]["StepIdentifier"], list):
        steps_id = [
            step["Id"]
            for step in config_data["Scenario"]["StepIdentifiers"]["StepIdentifier"]
        ]
    else:
        steps_id = [config_data["Scenario"]["StepIdentifiers"]["StepIdentifier"]["Id"]]
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
        step_obj = Step(
            name=step_info["Step"]["DisplayName"],
            id=step_info["Step"]["StepIdentifier"]["Id"],
        )
        step_obj.pos = StepPos.model_validate(
            step_metadata["StepMetadata"]["LocalPositionInScenario"]
        )
        step_obj.is_origin = bool(
            step_metadata["StepMetadata"]["IsScenarioOrigin"].lower() == "true"
        )
        if step_info["Step"]["ComponentMetadataIdentifiers"] is None:
            comp_id = []
        else:
            if isinstance(
                step_info["Step"]["ComponentMetadataIdentifiers"]["ItemIdentifier"],
                list,
            ):
                comp_id = [
                    component["Id"]
                    for component in step_info["Step"]["ComponentMetadataIdentifiers"][
                        "ItemIdentifier"
                    ]
                ]
            else:
                comp_id = [
                    step_info["Step"]["ComponentMetadataIdentifiers"]["ItemIdentifier"][
                        "Id"
                    ]
                ]
        for component in comp_id:
            new_component = parseComponent(component_data, links_data, component, scenario_path)
            if new_component is not None:
                uuids.append(new_component.id)
                step_obj.add(new_component)
        if step_info["Step"]["MediaMetadataIdentifiers"] is None:
            media_ids = []
        else:
            if isinstance(
                step_info["Step"]["MediaMetadataIdentifiers"]["ItemIdentifier"], list
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
            new_component = parseMedia(media_data, animation_data, media, scenario_path)
            uuids.append(new_component.id)
            step_obj.add(new_component)
        scenario.add_step(step_obj, auto_pos=False)
    step_ids = [st.id for st in scenario.steps]
    # for step in scenario.steps:
    #     for comp in step.items:
    #         if hasattr(comp, "to"):
    #             if comp.to is not None:
    #                 comp.to = scenario.steps[step_ids.index(comp.to)]
    flowapi.tools.uuid_list.update(uuids)
    return scenario
