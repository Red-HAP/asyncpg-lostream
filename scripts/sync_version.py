#!/usr/bin/env python3
#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import configparser
import pathlib

from packaging import version

MY_DIR = pathlib.Path(__file__).parent
BASE_DIR = MY_DIR.parent
SETUP_CFG = BASE_DIR / "setup.cfg"
ASYNCPG_LOSTREAM = BASE_DIR / "src" / "asyncpg_lostream" / "__version__"


setup_config = configparser.ConfigParser()
setup_config.read(SETUP_CFG)
if not ASYNCPG_LOSTREAM.exists():
    mod_version = "0.0.0"
else:
    mod_version = open(ASYNCPG_LOSTREAM, "rt").read().strip()

cfg_ver = version.Version(setup_config["metadata"]["version"])
mod_ver = version.Version(mod_version)

if cfg_ver != mod_ver:
    print(f"Copying setup.cfg version {cfg_ver} to __version__ file")
    with open(ASYNCPG_LOSTREAM, "wt") as ver_file:
        ver_file.write(setup_config["metadata"]["version"])
