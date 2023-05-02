import os
import shutil
import ctypes
from ctypes import wintypes
from pathlib import Path

try:
    import winreg
except ImportError:
    import _winreg as winreg

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

FONTS_REG_PATH = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"

HWND_BROADCAST = 0xFFFF
SMTO_ABORTIFHUNG = 0x0002
WM_FONTCHANGE = 0x001D
GFRI_DESCRIPTION = 1
GFRI_ISTRUETYPE = 3

if not hasattr(wintypes, "LPDWORD"):
    wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

user32.SendMessageTimeoutW.restype = wintypes.LPVOID
user32.SendMessageTimeoutW.argtypes = (
    wintypes.HWND,  # hWnd
    wintypes.UINT,  # Msg
    wintypes.LPVOID,  # wParam
    wintypes.LPVOID,  # lParam
    wintypes.UINT,  # fuFlags
    wintypes.UINT,  # uTimeout
    wintypes.LPVOID,
)  # lpdwResult

gdi32.AddFontResourceW.argtypes = (wintypes.LPCWSTR,)  # lpszFilename

# http://www.undocprint.org/winspool/getfontresourceinfo
gdi32.GetFontResourceInfoW.argtypes = (
    wintypes.LPCWSTR,  # lpszFilename
    wintypes.LPDWORD,  # cbBuffer
    wintypes.LPVOID,  # lpBuffer
    wintypes.DWORD,
)  # dwQueryType


SYSTEM_FONT_PATH = Path(os.environ["SystemRoot"]).joinpath("Fonts")


def check_font_installed(font: Path) -> bool:
    installed_path = SYSTEM_FONT_PATH.joinpath(font.name)
    return installed_path.exists()


def install_font_windows(font: Path):
    """Install font in Windows. Automatically notifies running programs and updates the registry.

    Args:
        font: Path to the font file.
    """
    # copy the font to the Windows Fonts folder
    dst_path = SYSTEM_FONT_PATH.joinpath(font.name)
    if dst_path.exists():
        print("Font already installed")
        return
    shutil.copy(font, dst_path)

    # load the font in the current session
    if not gdi32.AddFontResourceW(str(dst_path)):
        dst_path.unlink(missing_ok=True)
        raise WindowsError('AddFontResource failed to load "%s"' % font)

    # notify running programs
    user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_FONTCHANGE, 0, 0, SMTO_ABORTIFHUNG, 1000, None
    )

    # store the fontname/filename in the registry
    filename = dst_path.name
    fontname = os.path.splitext(filename)[0]
    # try to get the font's real name
    cb = wintypes.DWORD()
    if gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), None, GFRI_DESCRIPTION):
        buf = (ctypes.c_wchar * cb.value)()
        if gdi32.GetFontResourceInfoW(
            filename, ctypes.byref(cb), buf, GFRI_DESCRIPTION
        ):
            fontname = buf.value

    is_truetype = wintypes.BOOL()
    cb.value = ctypes.sizeof(is_truetype)

    gdi32.GetFontResourceInfoW(
        filename, ctypes.byref(cb), ctypes.byref(is_truetype), GFRI_ISTRUETYPE
    )
    if is_truetype:
        fontname += " (TrueType)"
    with winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE, FONTS_REG_PATH, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, fontname, 0, winreg.REG_SZ, filename)
