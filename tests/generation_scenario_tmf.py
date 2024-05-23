from pathlib import Path
import flowapi
import flowapi.scenario_parser

scenario = flowapi.Scenario(name="sqdqsdsqd")
step_connection = scenario.add_step(flowapi.Step(name="Connection", origin=True))
step_connection.set_pos_grid(0, 5)

step_eqt_1 = scenario.add_step(flowapi.Step(name="Eqt1"))
step_eqt_1.set_pos_grid(1, 6)
step_eqt_1_vue_2d = scenario.add_step(flowapi.Step(name="Eqt1-Vue2D"))
step_eqt_1_vue_2d.set_pos_grid(2, 7)
step_eqt_1_vue_3d = scenario.add_step(flowapi.Step(name="Eqt1-Vue3D"))
step_eqt_1_vue_3d.set_pos_grid(2, 6)
step_eqt_1_planning_interventions = scenario.add_step(
    flowapi.Step(name="Eqt1-PlanningInterventions")
)
step_eqt_1_planning_interventions.set_pos_grid(2, 5)

step_intervention_1 = scenario.add_step(flowapi.Step(name="Intervention1"))
step_intervention_1.set_pos_grid(1, 8.5)
step_intervention_1_autorisations = scenario.add_step(
    flowapi.Step(name="Intervention1-Autorisations")
)
step_intervention_1_autorisations.set_pos_grid(2, 9)
step_intervention_1_procedure = scenario.add_step(
    flowapi.Step(name="Intervention1-Procedure")
)
step_intervention_1_procedure.set_pos_grid(2, 8)

step_assistance_1_2d = scenario.add_step(flowapi.Step(name="Assistance1-2D"))
step_assistance_1_2d.set_pos_grid(3, 8)
step_assistance_1_Video = scenario.add_step(flowapi.Step(name="Assistance1-Video"))
step_assistance_1_Video.set_pos_grid(3, 7)
step_assistance_1_RM = scenario.add_step(flowapi.Step(name="Assistance1-RM"))
step_assistance_1_RM.set_pos_grid(3, 6)


step_eqt_2 = scenario.add_step(flowapi.Step(name="Eqt2"))
step_eqt_2.set_pos_grid(1, 3)
step_intervention_2 = scenario.add_step(flowapi.Step(name="Intervention2"))
step_intervention_2.set_pos_grid(1, 5)
step_intervention_2_procedure = scenario.add_step(
    flowapi.Step(name="Intervention2-Procedure")
)
step_intervention_2_procedure.set_pos_grid(2, 4)
step_assistance_2_2d = scenario.add_step(flowapi.Step(name="Assistance2-2D"))
step_assistance_2_2d.set_pos_grid(3, 4)
step_assistance_2_RM = scenario.add_step(flowapi.Step(name="Assistance2-RM"))
step_assistance_2_RM.set_pos_grid(3, 3)


# Composant ui
panneau_equipement = flowapi.LinearComponentArray(
    number_per_column=3, row_pitch=0.2, col_pitch=0.2
)
panneau_equipement_boutons = {
    "2D_assistance": flowapi.BoutonText(
        name="B_2DAssistance", value="Assistance 2D"
    ).set_size(0.1),
    "3D_assistance": flowapi.BoutonText(
        name="B_3DAssistance", value="Assistance 3D"
    ).set_size(0.1),
    "Video_assistance": flowapi.BoutonText(
        name="B_VideoAssistance", value="Assistance 3D"
    ).set_size(0.1),
    "Oral_Report": flowapi.BoutonText(
        name="B_OralReport", value="Rapport Oral"
    ).set_size(0.1),
    "Procedure": flowapi.BoutonText(name="B_Procedure", value="Procedure").set_size(
        0.1
    ),
    # "YSpot": flowapi.BoutonText("Bouton_YSpot","YSpot").set_size(0.1),
}
panneau_equipement.set_components(list(panneau_equipement_boutons.values()))

# Setup Connection
position_bouton_connection = {"x": 0, "y": 0, "z": 0}
bouton_connect_eqt_1 = step_connection.add(
    flowapi.BoutonText(
        name="Connection-Bouton-Eqt1", value="Equipement 1"
    ).set_position(**position_bouton_connection)
)
bouton_connect_eqt_1.target(step_eqt_1)
bouton_connect_eqt_2 = step_connection.add(
    flowapi.BoutonText(
        name="Connection-Bouton-Eqt2", value="Equipement 2"
    ).set_position(**position_bouton_connection)
)
bouton_connect_eqt_2.target(step_eqt_2)
panneau_assistance = flowapi.LinearComponentArray(1, 0.1, 0.1)
panneau_assistance_buttons = {
    "2D": flowapi.BoutonText(name="B_Assistance1-2D", value="").target(
        step_assistance_1_2d
    ),
    "Video": flowapi.BoutonText(name="B_Assistance1-Video", value="").target(
        step_assistance_1_Video
    ),
    "RM": flowapi.BoutonText(name="B_Assistance1-RM", value="").target(
        step_assistance_1_RM
    ),
}
panneau_assistance.set_components(list(panneau_assistance_buttons.values()))

# Setup Eqt 1
list_keys_bouton_equipement = list(panneau_equipement_boutons.keys())
panneau_equipement_step_eqt_1 = step_eqt_1.add(panneau_equipement, clone=True)
panneau_equipement_step_eqt_1.components[
    list_keys_bouton_equipement.index("2D_assistance")
].target(step_eqt_1_vue_2d)
panneau_equipement_step_eqt_1.components[
    list_keys_bouton_equipement.index("3D_assistance")
].target(step_eqt_1_vue_3d)
panneau_equipement_step_eqt_1.components[
    list_keys_bouton_equipement.index("Video_assistance")
].target(step_eqt_1_planning_interventions)
step_eqt_1.add(panneau_assistance, clone=True)

# Setup Eqt1 vue 2d
step_eqt_1_vue_2d.add(panneau_assistance, clone=True)
# Setup Eqt1 vue 3d
step_eqt_1_vue_3d.add(panneau_assistance, clone=True)
# Setup Intervention1 procedure
step_intervention_1_procedure.add(panneau_assistance, clone=True)

# Setup Eqt

# Autorisations 1
step_intervention_1_autorisations.add_placeholder("I_Intervention1-Autorisations_UI-KO")
step_intervention_1_autorisations.add_placeholder("I_Intervention1-Autorisations_UI-OK")


placeholder_array = flowapi.LinearComponentArray(1, 0.2, 0.2)
placeholders = [
    flowapi.Media.get_placeholder(name="alert"),
    flowapi.Media.get_placeholder(name="procedure"),
    flowapi.Media.get_placeholder(name="autorisation"),
    flowapi.Media.get_placeholder(name="warning"),
]
placeholder_array.set_components(placeholders)
step_connection.add(placeholder_array)


SCENARIO_PATH = Path.home().joinpath(
    "C:\\Users\\EL221079\\AppData\\LocalLow\\HoloForge\\Flow\\000000000000\\Scenarios"
)
SCENARIO_PATH = Path(__file__).parent
SCENARIO_PATH.mkdir(exist_ok=True, parents=True)
path = scenario.save_scenario(SCENARIO_PATH)
open("test_dump_scenario.json", "w").write(scenario.model_dump_json(indent=2))

scenario = flowapi.scenario_parser.parseScenario(path)
scenario.id = "00000000"
scenario.name = "Scenario cloné"
scenario.save_scenario(SCENARIO_PATH)
open("test_dump_scenario_clone.json", "w").write(scenario.model_dump_json(indent=2))
