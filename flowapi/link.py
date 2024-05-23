from pydantic import BaseModel, Field

from flowapi.items import Component
from .step import Step
from .tools import get_uuid


class Link(BaseModel):
    from_step: Step
    dest_step: Step
    source_component: Component
    id: str = Field(default_factory=get_uuid)

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
        new_link = Link(
            from_step=link_dict["StepIdentifier"]["Id"],
            dest_step=link_dict["DestinationIdentifier"]["Id"],
            source_component=link_dict["ComponentMetadataIdentifier"]["Id"],
        )
        return new_link
