def print_with_color(text, color):
    color_codes = {
        "black": "30",
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "white": "37",
        "reset": "0",
    }

    print(f"\033[{color_codes[color]}m{text}\033[0m")
