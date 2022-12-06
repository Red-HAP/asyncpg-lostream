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

# Makefile for standardized tasks.

help:
	@echo "Targets for asyncpg-lostream development:"
	@echo "  start_db             : Start up the test database container (uses port 5432)"
	@echo "  stop_db              : Stop the test database container (destroys the container volume also)"
	@echo "  verify_db            : Verify that the database in the container is accepting connections"
	@echo "  run_tests            : Execute 'verify_db', then execute pytest"
	@echo "  clean                : Execute 'stop_db' then remove build output disk files"
	@echo "  test                 : Execute 'clean', 'start_db', 'run_tests', 'stop_db'"
	@echo "  sync_version         : Sync the module version file to the version in setup.cfg"
	@echo "  build                : Execute 'clean', 'test', 'sync_version' then execute the build"
	@echo "  verify_dist_dir      : Ensure that the './dist' dir exists"
	@echo "  verify_dist_contents : Ensure that the './dist' dir is not empty"
	@echo "  verify_artifacts     : Execute 'verify_dist_dir', 'verify_dist_contents'"
	@echo "  twine_check          : Validate that the artifacts can be successfully uploaded to PyPI"
	@echo

all: clean
	@make build

verify_db:
	@printf "Checking availability of test database: "
	@while ! docker exec apl-postgres pg_isready -qd apl_postgres; do printf "."; sleep 1; done
	@echo " PostgreSQL database is available."

start_db:
	@echo "Starting up test database..."
	@docker-compose -f ./docker/docker-compose.yml up -d postgres

stop_db:
	@echo "Shutting down test database..."
	@docker-compose -f ./docker/docker-compose.yml down -v

clean: stop_db
	@echo "Cleaning up any former builds..."
	@rm -rf ./dist
	@rm -rf ./src/asyncpg_lostream.egg-info/

run_tests: verify_db
	@echo "Running tests..."
	@python -m pytest

test: clean start_db run_tests
	@make stop_db

sync_version:
	@echo "Syncing version from setup.cfg..."
	@./scripts/sync_version.py

build: clean test sync_version
	@echo "Building targets..."
	@python -m build

verify_dist_dir:
	@if [[ ! -d ./dist ]]; then echo "The 'dist' directory does not exist."; false; else true; fi

verify_dist_contents:
	@if [[ ! "$(shell ls -A ./dist)" ]]; then echo "The 'dist' directory is empty."; false; else true; fi

verify_artifacts: verify_dist_dir
	@make verify_dist_contents

twine_check: verify_artifacts
	@echo "Making sure targets will successfully upload."
	@python -m twine check --strict ./dist/*



# ==============================================================================
# ==============================================================================
# For the code owner(s) only!!
deploy_testpypi: twine_check
	@echo "Deploying to testpypi..."
	@python -m twine upload --verbose --repository testpypi dist/*

deploy_pypi: twine_check
	@echo "Deploying to testpypi..."
	@python -m twine upload --verbose --repository pypi dist/*
