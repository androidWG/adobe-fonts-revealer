import os
import platform
import argparse
import shutil
import tempfile
from pathlib import Path

from fontTools import ttLib

from fonts import install_font_windows, check_font_installed

WINDOWS_PATH = Path(os.getenv("APPDATA")).joinpath(r"Adobe\CoreSync\plugins\livetype\r")
MACOS_PATH = Path.home().joinpath(
    "Library/Application Support/Adobe/CoreSync/plugins/livetype/.r "
)


parser = argparse.ArgumentParser(
    prog="Adobe Fonts Revealer (Python Edition)",
    description="Copies all fonts currently active from Adobe Fonts to the current folder or installs them",
)

parser.add_argument("procedure", choices=["copy", "install"])
args = parser.parse_args()


def short_name(font) -> (str, str):
    """Get the short name from the font's names table

    Returns:
        names: String tuple with the family name and variant respectively
    """
    family = font["name"].getBestFamilyName()
    variant = font["name"].getBestSubFamilyName()

    return family, variant


if __name__ == "__main__":
    system = platform.system()
    if system == "Windows":
        path = WINDOWS_PATH
    elif system == "Darwin":
        path = MACOS_PATH
    else:
        raise NotImplementedError("Not running on a macOS or Windows system")

    for f in path.iterdir():
        if f.suffix != "":
            continue

        filepath = path.joinpath(f)
        otf = ttLib.TTFont(filepath)

        name = short_name(otf)
        filename = f"{name[0]}-{name[1]}.otf"

        match args.procedure:
            case "copy":
                print(
                    f"Copying font | Family: {name[0]:20} Variant: {name[1]} | To: {filename}"
                )
                shutil.copy(filepath, Path(os.curdir).absolute().joinpath(filename))
            case "install":
                with tempfile.TemporaryDirectory() as tmp:
                    new_path = Path(tmp).absolute().joinpath(filename)
                    if check_font_installed(new_path):
                        print(f"Skipping installed font | Family: {name[0]:20} Variant: {name[1]}")
                        continue

                    print(f"Installing font | Family: {name[0]:20} Variant: {name[1]}")

                    shutil.copy(filepath, new_path)
                    install_font_windows(new_path)

    print("Finished!")
