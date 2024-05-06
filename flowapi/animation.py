from .tools import get_uuid


class Animation:
    def __init__(self, path=None):
        self.id = get_uuid()
        self.media_path = path
        self.name = "Aucune animation"
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
        self.transformations_destination = {
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
                    "TemplatePath":self.media_path, 
                    "DisplayName": self.name,
                    "FlowAnimationType":"Default",
                    "Duration": self.duration,
                    "Transformations": {
                        "ValueTupleOfStringHFTransform":
                            [{
                                "Item1": None,
                                "Item2": self.transformations
                            },
                            {
                                "Item1": None,
                                "Item2": self.transformations_destination
                            }]
                    }
                },

        }
        return animation_dict
