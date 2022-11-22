import pathlib
import sys

module_path = pathlib.Path(__file__).parents[1] / "src"
sys.path.append(str(module_path))
