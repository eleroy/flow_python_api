import math


class LinearComponentArray:
    def __init__(self, number_per_column, row_pitch, col_pitch):
        self.components = []
        self.number_per_column = number_per_column
        self.position = {"x": 0, "y": 0, "z": 0}
        self.col_pitch = col_pitch
        self.row_pitch = row_pitch

    def update_component_positions(self):
        for i in range(len(self.components)):
            row_i = i // self.number_per_column
            position = self.position.copy()
            position["x"] += (i % self.number_per_column) * self.col_pitch
            position["y"] += row_i * self.row_pitch
            self.components[i].set_position(**position)

    def set_components(self, components):
        self.components = components
        self.update_component_positions()


class CircularComponentArray:
    def __init__(self, diameter):
        self.components = []
        self.position = {"x": 0, "y": 0, "z": 0}
        self.diameter = diameter


    def update_component_positions(self):
        for i in range(len(self.components)):
            x_offset = self.diameter*math.sin()
            row_i = i // self.number_per_column
            position = self.position.copy()
            position["x"] += (i % self.number_per_column) * self.col_pitch
            position["y"] += row_i * self.row_pitch
            self.components[i].set_position(**position)

    def set_components(self, components, clone=False):
        if clone:
            self.components = [component.clone() for component in components]
        else:
            self.components = components
        self.update_component_positions()


class ComponentGroup:
    def __init__(self):
        self.position = {"x": 0, "y": 0, "z": 0}
        self.rotation = {"x": 0, "y": 0, "z": 0}
        self.scale = {"x": 1, "y": 1, "z": 1}
        self.components = []
        self.relative_component_position = []

    def add_component(self, component, relative_position=None, clone = False):
        if relative_position is None:
            relative_position = {"x": 0, "y": 0, "z": 0}
        self.components.append(component.clone() if clone else component)
        self.relative_component_position.append(relative_position.copy())
        self.update_component_position()

    def update_component_position(self):
        for component in self.components:
            relative_pos = self.relative_component_position[self.components.index(component)]
            comp_pos = {
                "x":self.position["x"]+relative_pos["x"],
                "y":self.position["y"]+relative_pos["y"],
                "z":self.position["z"]+relative_pos["z"],
            }
            component.set_position(x=comp_pos["x"], y= comp_pos["y"], z=comp_pos["z"])

    def set_position(self,x=None, y=None, z=None):
        if x:
            self.position["x"] = x
        if y:
            self.position["y"] = y
        if z:
            self.position["z"] = z
        self.update_component_position()
        return self
