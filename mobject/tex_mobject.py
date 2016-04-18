from vectorized_mobject import VMobject
from svg_mobject import SVGMobject
from helpers import *

TEX_MOB_SCALE_VAL = 0.05

class TexMobject(SVGMobject):
    CONFIG = {
        "template_tex_file" : TEMPLATE_TEX_FILE,
        "stroke_width"      : 0,
        "fill_opacity"      : 1.0,
        "fill_color"        : WHITE,
        "should_center"     : True,
        "next_to_direction" : RIGHT,
        "next_to_buff"      : 0.2,
    }
    def __init__(self, expression, **kwargs):
        digest_config(self, kwargs, locals())
        VMobject.__init__(self, **kwargs)
        self.move_into_position()
        self.organize_submobjects()

    def generate_points(self): 
        if isinstance(self.expression, list):
            self.handle_list_expression()
        else:
            self.svg_file = tex_to_svg_file(
                "".join(self.expression),
                self.template_tex_file
            )
            SVGMobject.generate_points(self)


    def handle_list_expression(self):
        #TODO, next_to not sufficient?
        subs = [
            TexMobject(expr)
            for expr in self.expression
        ]
        for sm1, sm2 in zip(subs, subs[1:]):
            sm2.next_to(
                sm1,
                self.next_to_direction, 
                self.next_to_buff
            )
        self.submobjects = subs
        return self

    def organize_submobjects(self):
        self.submobjects.sort(
            lambda m1, m2 : int((m1.get_left()-m2.get_left())[0])
        )

    def move_into_position(self):
        self.center()
        self.scale(TEX_MOB_SCALE_VAL)
        self.init_colors()


class TextMobject(TexMobject):
    CONFIG = {
        "template_tex_file" : TEMPLATE_TEXT_FILE,
    }


class Brace(TexMobject):
    CONFIG = {
        "buff" : 0.2,
    }
    TEX_STRING = "\\underbrace{%s}"%(14*"\\quad")
    def __init__(self, mobject, direction = DOWN, **kwargs):
        TexMobject.__init__(self, self.TEX_STRING, **kwargs)
        angle = -np.arctan2(*direction[:2]) + np.pi
        mobject.rotate(-angle)
        left  = mobject.get_corner(DOWN+LEFT)
        right = mobject.get_corner(DOWN+RIGHT)
        self.stretch_to_fit_width(right[0]-left[0])
        self.shift(left - self.points[0] + self.buff*DOWN)
        for mob in mobject, self:
            mob.rotate(angle)
    
def tex_hash(expression):
    return str(hash(expression))

def tex_to_svg_file(expression, template_tex_file):
    image_dir = os.path.join(TEX_IMAGE_DIR, tex_hash(expression))
    if os.path.exists(image_dir):
        return get_sorted_image_list(image_dir)
    tex_file = generate_tex_file(expression, template_tex_file)
    dvi_file = tex_to_dvi(tex_file)
    return dvi_to_svg(dvi_file)


def generate_tex_file(expression, template_tex_file):
    result = os.path.join(TEX_DIR, tex_hash(expression))+".tex"
    if not os.path.exists(result):
        print "Writing \"%s\" to %s"%(
            "".join(expression), result
        )
        with open(template_tex_file, "r") as infile:
            body = infile.read()
            body = body.replace(TEX_TEXT_TO_REPLACE, expression)
        with open(result, "w") as outfile:
            outfile.write(body)
    return result

def tex_to_dvi(tex_file):
    result = tex_file.replace(".tex", ".dvi")
    if not os.path.exists(result):
        commands = [
            "latex", 
            "-interaction=batchmode", 
            "-output-directory=" + TEX_DIR,
            tex_file,
            "> /dev/null"
        ]
        #TODO, Error check
        os.system(" ".join(commands))
    return result

def dvi_to_svg(dvi_file, regen_if_exists = False):
    """
    Converts a dvi, which potentially has multiple slides, into a 
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    result = dvi_file.replace(".dvi", ".svg")
    if not os.path.exists(result):
        commands = [
            "dvisvgm",
            dvi_file,
            "-n",
            "-v",
            "0",
            "-o",
            result,
            "> /dev/null"
        ]
        os.system(" ".join(commands))
    return result














