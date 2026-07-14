"""
Locates the Path of Exile 2 Client.txt log file, trying multiple
strategies in order: saved config, common default install paths,
and the Windows registry.
"""
import logging
import winreg
from pathlib import Path
from typing import Callable

from zarokh.config import ConfigManager

logger = logging.getLogger(__name__)

CONFIG_KEY = "client_txt_path"

DEFAULT_PATHS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Path of Exile 2\logs\Client.txt",
    r"C:\Program Files (x86)\Grinding Gear Games\Path of Exile 2\logs\Client.txt",
]

REGISTRY_KEY_PATH = r"SOFTWARE\Grinding Gear Games\Path of Exile 2"


def find_client_log_path(
    config: ConfigManager,
    default_paths: list[str] | None = None,
    registry_lookup: Callable[[], str | None] | None = None,
) -> str | None:
    """
    Tries to locate Client.txt using, in order:
    1. A path already saved in config.
    2. Common default install locations.
    3. The Windows registry install location.

    `default_paths` and `registry_lookup` can be overridden (e.g. in
    tests) to avoid depending on the real filesystem or Windows
    registry of the machine running the code.
    """
    if default_paths is None:
        default_paths = DEFAULT_PATHS
    if registry_lookup is None:
        registry_lookup = _find_path_in_registry

    saved_path = config.get(CONFIG_KEY)
    if saved_path and Path(saved_path).exists():
        return saved_path

    for candidate in default_paths:
        if Path(candidate).exists():
            config.set(CONFIG_KEY, candidate)
            return candidate

    registry_path = registry_lookup()
    if registry_path and Path(registry_path).exists():
        config.set(CONFIG_KEY, registry_path)
        return registry_path

    return None


def _find_path_in_registry() -> str | None:
    """Looks up the PoE2 install location in the Windows registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_KEY_PATH) as key:
            install_path = winreg.QueryValueEx(key, "InstallLocation")[0]
            return str(Path(install_path) / "logs" / "Client.txt")
    except OSError as e:
        logger.info("PoE2 registry key not found: %s", e)
        return None