from .tools import get_uuid


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
