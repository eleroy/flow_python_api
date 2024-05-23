from pydantic import BaseModel, Field
from .tools import FullPosition, get_uuid


class Animation(BaseModel):
    media_path: str | None = None
    id: str = Field(default_factory=get_uuid)
    name: str = "Aucune animation"
    duration: float = 0
    transformations: FullPosition = Field(default_factory=FullPosition)
    transformations_destination: FullPosition = Field(default_factory=FullPosition)

    def get_dict(self):
        animation_dict = {
            "FlowAnimation": {
                "AnimationIdentifier": {"Id": self.id},
                "TemplatePath": self.media_path,
                "DisplayName": self.name,
                "FlowAnimationType": "Default",
                "Duration": self.duration,
                "Transformations": {
                    "ValueTupleOfStringHFTransform": [
                        {"Item1": None, "Item2": self.transformations.model_dump()},
                        {
                            "Item1": None,
                            "Item2": self.transformations_destination.model_dump(),
                        },
                    ]
                },
            },
        }
        return animation_dict


if __name__ == "__main__":
    anim = Animation()
    print(anim)
    print(anim.get_dict())
