import argparse
import json
from pathlib import Path
import pypugjs
import weasyprint
from PIL import Image, ImageChops
import jinja2
from pdf2image import convert_from_path, convert_from_bytes


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    # diff = ImageChops.add(diff, diff, 2.0, -100)
    # Bounding box given as a 4-tuple defining the left, upper, right, and lower pixel coordinates.
    # If the image is completely empty, this method returns None.
    bbox = diff.getbbox(alpha_only=True)
    if bbox:
        return im.crop(bbox)
def render_component(template_name, context, output_file="test.png"):
    env = jinja2.Environment(
                    loader=jinja2.FileSystemLoader(Path(__file__).parent.joinpath("templates").absolute()),
                    extensions=["pypugjs.ext.jinja.PyPugJSExtension"],
                )
    template = env.get_template(template_name)
    html = template.render(context)
    css = [weasyprint.CSS(filename=Path(__file__).parent.joinpath("semantic.min.css")),
           weasyprint.CSS(filename=Path(__file__).parent.joinpath("style.css"))
           ]
    weasyprint.HTML(string=html).write_pdf("test.pdf", stylesheets=css)
    images = convert_from_path("test.pdf", output_file=Path(__file__).parent.joinpath("test.png"),
                               poppler_path=str(Path(__file__).parent.joinpath("poppler").absolute()), transparent=True,
                               dpi=400)
    image = trim(images[0])
    image.save(output_file, 'PNG')
    return html


# etapes = {"etapes":
#               [
#                   {"numero":"1",
#                    "description":"Retirer le capot de protection",
#                    "risques":"Pas de risques",
#                    "equipement": "Servovalve"
#                    },
#                     {"numero":"2",
#                     "description":"Regler le jeu",
#                    "risques":"Pas de risques",
#                    "equipement": "Servovalve"
#                    }
#               ]
# }
# with open("test.html", "w") as fp:
#     fp.write(render_component("procedure.pug",etapes))
# test_pug_js = """
# html
#     head
#         link(rel="stylesheet",href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.5.0/semantic.min.css")
#     body
#         .ui.container
#           .ui.icon.message.yellow.block-center
#             i.exclamation.circle.icon
#             .content
#               .header This is an important message, as per the exclamation mark.
#               p.
#                 You can add content to your message explaining why it is important and
#                 what the reader can do to de-importantize the situation.
#         table.ui.celled.striped.table
#             thead
#                 tr
#                     th Etape
#                     th Risques
#                     th Equipement
#                     th Actions
#             tbody
#                 tr
#                     td
#                         i.circular.inverted.green.user.icon
#                         |  Chef de service
#                     td Autorisation accordée
#
#
# """

def ui_generator_command_line():
    parser = argparse.ArgumentParser(
        prog='ui_generator',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('filename', help='a json filename containing the ui info')
    args = parser.parse_args()
    file_path = Path(args.filename).parent
    try:
        ui_info = json.load(open(args.filename, "r"))
    except:
        return None
    available_templates = [Path(file).name for file in Path(__file__).parent.joinpath("templates").iterdir()]
    if not ui_info["template"]+".pug" in available_templates:
        print("Template not found")
        return None
    render_component(ui_info["template"]+".pug", context= ui_info["context"] if "context" in ui_info else None, output_file=file_path.joinpath(ui_info["template"]+".png").absolute())