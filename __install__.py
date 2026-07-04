from streamcontroller_plugin_toold.installation_helpers import create_venv
from os.path import join, abspath, dirname

toplevel = dirname(abspath(__file__))
create_venv(
    join(toplevel, "backend", ".venv", join(toplevel, "backend", "requirements.txt"))
)