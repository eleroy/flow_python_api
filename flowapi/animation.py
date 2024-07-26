from pydantic import BaseModel, Field
from .tools import FullPosition, get_uuid

from typing import TypedDict, List, Union
EulerAnglesOrPositionOrScale = TypedDict("EulerAnglesOrPositionOrScale", {"x": str, "y": str, "z": str})
ValueTupleOfStringHFTransform = TypedDict("ValueTupleOfStringHFTransform", {"Item1": Union[None, str], "Item2": TypedDict("Item2", {"position": EulerAnglesOrPositionOrScale, "rotation": TypedDict("Rotation", {"x": str, "y": str, "z": str, "w": str, "eulerAngles": EulerAnglesOrPositionOrScale}), "scale": EulerAnglesOrPositionOrScale})})
TemplatePathOrAnimationIdentifier = TypedDict("TemplatePathOrAnimationIdentifier", {"Id": str})
FlowAnimationDictType = TypedDict("FlowAnimation", {"AnimationIdentifier": TemplatePathOrAnimationIdentifier, "TemplatePath": TemplatePathOrAnimationIdentifier, "DisplayName": str, "FlowAnimationType": str, "Duration": str, "Transformations": TypedDict("Transformations", {"ValueTupleOfStringHFTransform": Union[ValueTupleOfStringHFTransform, List[ValueTupleOfStringHFTransform]]})})


class ValueTupleOfStringHFTransform(BaseModel):
    Item1: str | None = None
    Item2: FullPosition = Field(default_factory=FullPosition)

class Animation(BaseModel):
    media_path: str | None = None
    id: str = Field(default_factory=get_uuid)
    name: str = "Aucune animation"
    duration: float = 0
    transformations: list[ValueTupleOfStringHFTransform] |  ValueTupleOfStringHFTransform = Field(default_factory=lambda: [ValueTupleOfStringHFTransform(), ValueTupleOfStringHFTransform()])
    animation_type: str = "Default"
    def get_dict(self):
        animation_dict = {
            "FlowAnimation": {
                "AnimationIdentifier": {"Id": self.id},
                "TemplatePath": {"Id":self.media_path},
                "DisplayName": self.name,
                "FlowAnimationType": self.animation_type,
                "Duration": self.duration,
                "Transformations": {
                    "ValueTupleOfStringHFTransform": ([trans.model_dump() for trans in self.transformations] if isinstance(self.transformations, list) else self.transformations.model_dump())
                },
            },
        }
        return animation_dict

    @staticmethod
    def parse(animation_dict:FlowAnimationDictType):
        tf = []
        for trans in animation_dict["Transformations"]["ValueTupleOfStringHFTransform"]:
            tf.append(ValueTupleOfStringHFTransform.model_validate(trans)) 
        return Animation(id=animation_dict["AnimationIdentifier"]["Id"],
                    media_path=animation_dict["TemplatePath"]["Id"],
                    name=animation_dict["DisplayName"],
                    duration=float(animation_dict["Duration"]),
                    transformations=tf,
                    animation_type=animation_dict["FlowAnimationType"]
                    )
    


if __name__ == "__main__":
    anim = Animation()
    print(anim)
    print(anim.get_dict())
