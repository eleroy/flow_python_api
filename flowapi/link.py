from .step import Step
from .tools import get_uuid


class Link:
    def __init__(self, from_step, dest_step, source_component):
        self.id = get_uuid()
        self.from_step: Step = from_step
        self.dest_step: Step = dest_step
        self.source_component = source_component

    def get_xml(self):
        link_dict = {
            "LinkIdentifier": {"Id": self.id},
            "StepIdentifier": {"Id": self.from_step.id},
            "ComponentMetadataIdentifier": {"Id": self.source_component.id},
            "PropertyIdentifier": {"Id": self.source_component.property_identifier},
            "DestinationIdentifier": {"Id": self.dest_step.id},
        }
        return link_dict

    @staticmethod
    def from_dict(link_dict):
        new_link = Link(link_dict["StepIdentifier"]["Id"],
                        link_dict["DestinationIdentifier"]["Id"],
                        link_dict["ComponentMetadataIdentifier"]["Id"],
                        )

        return

