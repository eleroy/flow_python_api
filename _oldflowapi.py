import uuid
from pathlib import Path
from cairosvg import svg2png

from flowapi import BoutonText, Media
from flowapi.scenario_parser import parseScenario

test_path = Path(r"C:\Users\EL221079\AppData\LocalLow\HoloForge\Flow\000000000000\Scenarios\280a2a8f")
# test_path = Path(r"C:\Users\EL221079\AppData\LocalLow\HoloForge\Flow\000000000000\Scenarios\00000001")


scenario = parseScenario(test_path)
scenario.save_scenario()
exit()
def generate_odm_pane(text, image_id=None):
    uuid_image = str(uuid.uuid4()) if image_id is None else image_id
    with open("odm.svg","r",encoding="utf-8") as f:
        image_svg = f.read()
    image_svg=image_svg.replace("$ODM", text)
    svg2png(image_svg.encode(encoding="utf-8"),write_to=uuid_image+'.png')
    return Path(uuid_image+'.png')

class PanneauBouton(ComponentGroup):
    def __init__(self, title_panneau):
        super().__init__()
        self.panneau_image_path = generate_odm_pane(title_panneau)
        self.panneau_image = Media(self.panneau_image_path)
        self.bouton_1 = BoutonText("->", "1")
        self.bouton_2 = BoutonText("X", "2")
        self.bouton_3 = BoutonText("C", "3")
        self.bouton_4 = BoutonText("4", "4")
        self.add_component(self.panneau_image)
        self.add_component(self.bouton_1, relative_position={"x":0.3, "y":0.15, "z":-0.05})
        self.add_component(self.bouton_2, relative_position={"x":0.3, "y":0.013, "z":-0.05})
        self.add_component(self.bouton_3, relative_position={"x":0.3, "y":-0.125, "z":-0.05})
        self.add_component(self.bouton_4, relative_position={"x":0.3, "y":-0.27, "z":-0.05})

class Dialog(Media):
    def __init__(self, color = "#FF0000", message="Dialog"):
        uuid_image = str(uuid.uuid4())
        with open("dialog.svg", "r", encoding="utf-8") as f:
            image_svg = f.read()
        image_svg = image_svg.replace("$Message", message).replace("#000000", color)
        svg2png(image_svg.encode(encoding="utf-8"), write_to=uuid_image + '.png')
        super().__init__(Path(uuid_image + '.png'))
        self.set_width(2)

new_scenario = Scenario("1000 Buttons scenario", id="00000004")
# On ajoute les étapes
steps = [] # La liste de toutes les étapes pour pouvoir y acceder et les modifier ensuite
for i in range(100):
    steps.append(new_scenario.add_step(Step(f"etape_{i}")))
# On crée une grille de 10 boutons, chaque bouton a une étape en target
boutons = []
for i in range(100):
    boutons.append(BoutonText(value=f"Bouton {i}").target(steps[i]))
# On arrange ces boutons selon une grille de 5 colonne avec un pitch entre les ligne de 0.2m idem entre les colonnes
bouton_array = LinearComponentArray(5, 0.2, 0.2)
bouton_array.set_components(boutons) # On ajoute les boutons à la matrice de componsants

# A chaque étape on ajoute la grille de bouton. Il faut cloner la grille car on ne peut pas utiliser
# le meme bouton deux fois dans le scénario (même dans des étapes differentes)
# steps[0].add(PanneauBouton("Panneau 1").set_position(x=0))
# steps[0].add(PanneauBouton("Panneau 2").set_position(x=1))
# steps[0].add(PanneauBouton("Panneau 3").set_position(x=2))
# steps[0].add(Dialog("#FF0000", "ATTENTION GROS GROS PROBLEME").set_position(y=1))
# steps[0].add(Dialog("#FF9955", "ATTENTION MOYEN PROBLEME").set_position(x=2,y=1))
# steps[0].add(Dialog("#3771C8", "JUSTE UNE INFO COMME CA").set_position(x=4,y=1))
for i,step in enumerate(steps):
    step.add(bouton_array, clone=True)
# On enregistre le scénario
new_scenario.save_scenario()
