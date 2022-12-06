import pathlib

MY_DIR = pathlib.Path(__file__).parent

VERSION = open(MY_DIR / "__version__", "rt").read().strip()
