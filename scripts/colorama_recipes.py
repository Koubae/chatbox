"""
Colorama: https://github.com/tartley/colorama
Collection of colorama Recipes to quick find what you need
"""

from colorama import Fore, Back, Style


# Set colorama Back to default
default_style = lambda : print(Style.RESET_ALL)


def from_docs():

    print(Fore.RED + 'some red text')
    print(Back.GREEN + 'and with a green background')
    print(Style.DIM + 'and in dim text')
    print(Style.RESET_ALL)
    print('back to normal now')

    print('\033[31m' + 'some red text')
    print('\033[39m') # and reset to default color


def recipe_colors_front():
    default_style()
    print("------------- < COLORAMA SHOWCASE: Front Color > -------------")
    colors = [attr for attr in dir(Fore) if not attr.startswith("_")]
    colors_default = [c for c in colors if not c.startswith("LIGHT")]
    colors_light = [c for c in colors if c.startswith("LIGHT")]
    print(colors_default)
    print(colors_light)

    for color in colors_default:
        print(getattr(Fore, color), f"Color={color}")
    default_style()
    print("---------- Print Light colors")
    for color in colors_light:
        print(getattr(Fore, color), f"Color={color}")
    default_style()



def recipe_colors_back():
    default_style()
    print("------------- < COLORAMA SHOWCASE: Back Color > -------------")
    colors = [attr for attr in dir(Back) if not attr.startswith("_")]
    colors_default = [c for c in colors if not c.startswith("LIGHT")]
    colors_light = [c for c in colors if c.startswith("LIGHT")]
    print(colors_default)
    print(colors_light)
    for color in colors_default:
        print(getattr(Back, color), f"Color={color}")
    default_style()
    print("---------- Print Light colors")
    for color in colors_light:
        print(getattr(Back, color), f"Color={color}")
    default_style()


def recipe_styles():
    default_style()
    styles = [attr for attr in dir(Style) if not attr.startswith("_")]
    print(styles)
    print(Fore.RED) # Just to make it more visible
    for style in styles:
        print(getattr(Style, style) + f'------ STYLE={style}')

    default_style()


def recipe_01():
    default_style()
    print(Back.LIGHTWHITE_EX + Fore.BLACK )
    import this
    default_style()

def recipe_02():
    default_style()
    print(Back.BLACK + Fore.LIGHTWHITE_EX )
    # import antigravity
    import __hello__
    default_style()

if __name__ == '__main__':
    print() #just a placeholder...

    #from_docs()
    recipe_colors_front()
    recipe_colors_back()
    recipe_styles()
    recipe_01()
    recipe_02()