########################################
### Initialise dev environment
########################################

# Create a new poetry virtual environment with all the necessary dependencies installed.
# Once finished, `poetry shell` to enter the virtual environment
v := $(shell pip -V | grep virtualenvs)

.PHONY: new_env
new_env_dev: clean
	if [ -z "$v" ];\
	then\
		poetry install --with main,dev,test,docs --sync;\
		echo "Enter virtual environment with all development dependencies now: 'poetry shell'.";\
	else\
		echo "In a virtual environment! Exit first: 'exit'.";\
	fi
	pre-commit install

########################################
### Useful linting command
########################################

# Automatically runs black and isort to format the code, and runs flake8 and vulture checks
.PHONY: lint
lint: black ruff

########################################
### Tests
########################################

# Run all tests
.PHONY: test
test:
	coverage run -m pytest $(JUNOPY_TESTS_DIR) --doctest-modules
	$(MAKE) coverage-report

# Run all unit tests
.PHONY: unit-test
unit-test:
	coverage run -m pytest $(JUNOPY_TESTS_DIR) --doctest-modules -m "not integration"

# Run all integration tests
.PHONY: integration-test
integration-test:
	coverage run -m pytest $(JUNOPY_TESTS_DIR) --doctest-modules -m "integration"

# Produce the coverage report. Can see a report summary on the terminal.
# Detailed report on all modules are placed under /coverage-report
.PHONY: coverage-report
coverage-report:
	coverage report -m
	coverage html

########################################
### Automatic Styling
########################################

# Automatically formats the code
.PHONY: black
black:
	black $(PYTHON_CODE_DIRS) --exclude $(JUNOPY_PROTOS_DIR)

# Automatically sorts the imports
.PHONY: ruff
isort:
	ruff check $(PYTHON_CODE_DIRS)

########################################
### Code style checks
########################################

# Runs the black format checker
.PHONY: black-check
black-check:
	black --check --verbose $(PYTHON_CODE_DIRS) --exclude $(JUNOPY_PROTOS_DIR)

# Runs the isort format checker
.PHONY: isort-check
isort-check:
	isort --check-only --verbose $(PYTHON_CODE_DIRS)

# Runs flake8 checker
.PHONY: flake8
flake:
	flake8 $(PYTHON_CODE_DIRS)

########################################
### Update Poetry Lock
########################################

# Updates the poetry lock
poetry.lock: pyproject.toml
	poetry lock

########################################
### Clear the caches and temporary files
########################################

# clean the caches and temporary files and directories
.PHONY: clean
clean: clean-build clean-pyc clean-test clean-docs

.PHONY: clean-build
clean-build:
	rm -frv build/
	rm -frv dist/
	rm -frv .eggs/
	rm -frv pip-wheel-metadata
	find . -name '*.egg-info' -exec rm -frv {} +
	find . -name '*.egg' -exec rm -frv {} +

.PHONY: clean-docs
clean-docs:
	rm -frv site/

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -fv {} +
	find . -name '*.pyo' -exec rm -fv {} +
	find . -name '*~' -exec rm -fv {} +
	find . -name '__pycache__' -exec rm -frv {} +
	find . -name '.DS_Store' -exec rm -frv {} +

.PHONY: clean-test
clean-test:
	rm -frv .tox/
	rm -frv .coverage
	find . -name ".coverage*" -not -name ".coveragerc" -exec rm -frv "{}" \;
	rm -frv coverage_report/
	rm -frv .hypothesis
	rm -frv .pytest_cache
	rm -frv .mypy_cache/
	find . -name 'log.txt' -exec rm -frv {} +
	find . -name 'log.*.txt' -exec rm -frv {} +

########################################
### Generate protos and grpc files
########################################

# Constants
COSMOS_SDK_URL := https://github.com/fetchai/cosmos-sdk
COSMOS_SDK_VERSION := v0.18.0
COSMOS_SDK_DIR := build/cosmos-sdk-proto-schema

COSMOS_PROTO_URL := https://github.com/cosmos/cosmos-proto.git
COSMOS_PROTO_VERSION := v1.0.0-beta.3
COSMOS_PROTO_DIR := build/cosmos-proto-schema

JUNO_SDK_URL := https://github.com/CosmosContracts/juno
JUNO_SDK_VERSION := v13.0.0
JUNO_SDK_DIR := build/juno-sdk-proto-schema

WASMD_URL := https://github.com/CosmWasm/wasmd
WASMD_VERSION := v0.27.0
WASMD_DIR := build/wasm-proto-shema

IBCGO_URL := https://github.com/cosmos/ibc-go
IBCGO_VERSION := v2.2.0
IBCGO_DIR := build/ibcgo-proto-schema

JUNOPY_PROTOS_DIR := junopy/protos
JUNOPY_SRC_DIR := junopy

JUNOPY_TESTS_DIR := tests
JUNOPY_EXAMPLES_DIR := examples

PYTHON_CODE_DIRS := $(JUNOPY_SRC_DIR) $(JUNOPY_TESTS_DIR) $(JUNOPY_EXAMPLES_DIR)

ifeq ($(OS),Windows_NT)
	$(error "Please use the WSL (Windows Subsystem for Linux) on Windows platform.")
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
		OPEN_CMD := xdg-open
    endif
    ifeq ($(UNAME_S),Darwin)
		OPEN_CMD := open
    endif
endif

define unique
  $(eval seen :=)
  $(foreach _,$1,$(if $(filter $_,${seen}),,$(eval seen += $_)))
  ${seen}
endef
unique = $(if $1,$(firstword $1) $(call unique,$(filter-out $(firstword $1),$1)))

proto: fetch_proto_schema_source generate_proto_types generate_init_py_files

generate_proto_types: $(COSMOS_SDK_DIR) $(JUNO_SDK_DIR) $(WASMD_DIR) $(IBCGO_DIR)
	rm -frv $(JUNOPY_PROTOS_DIR)/*
	python -m grpc_tools.protoc --proto_path=$(WASMD_DIR)/proto --proto_path=$(WASMD_DIR)/third_party/proto  --python_out=$(JUNOPY_PROTOS_DIR) --grpc_python_out=$(JUNOPY_PROTOS_DIR) $(shell find $(WASMD_DIR) \( -path */proto/* -or -path */third_party/proto/* \) -type f -name *.proto)
	python -m grpc_tools.protoc --proto_path=$(IBCGO_DIR)/proto --proto_path=$(IBCGO_DIR)/third_party/proto  --python_out=$(JUNOPY_PROTOS_DIR) --grpc_python_out=$(JUNOPY_PROTOS_DIR) $(shell find $(IBCGO_DIR) \( -path */proto/* -or -path */third_party/proto/* \) -type f -name *.proto)
# ensure cosmos-sdk is last as previous modules may have duplicated proto models which are now outdated
	python -m grpc_tools.protoc --proto_path=$(COSMOS_SDK_DIR)/proto --proto_path=$(COSMOS_SDK_DIR)/third_party/proto  --python_out=$(JUNOPY_PROTOS_DIR) --grpc_python_out=$(JUNOPY_PROTOS_DIR) $(shell find $(COSMOS_SDK_DIR) \( -path */proto/* -or -path */third_party/proto/* \) -type f -name *.proto)
	python -m grpc_tools.protoc --proto_path=$(JUNO_SDK_DIR)/proto --proto_path=$(COSMOS_PROTO_DIR)/proto --proto_path=$(COSMOS_SDK_DIR)/proto --proto_path=$(COSMOS_SDK_DIR)/third_party/proto  --python_out=$(JUNOPY_PROTOS_DIR) --grpc_python_out=$(JUNOPY_PROTOS_DIR) $(shell find $(JUNO_SDK_DIR) \( -path */proto/* \) -type f -name *.proto)

fetch_proto_schema_source: $(COSMOS_SDK_DIR) $(COSMOS_PROTO_DIR) $(JUNO_SDK_DIR) $(WASMD_DIR) $(IBCGO_DIR)

.PHONY: generate_init_py_files
generate_init_py_files: generate_proto_types
	find $(JUNOPY_PROTOS_DIR)/ -type d -exec touch {}/__init__.py \;
	# restore root __init__.py as it contains code to have the proto files module available
	git restore $(JUNOPY_PROTOS_DIR)/__init__.py

$(SOURCE): $(COSMOS_SDK_DIR)

$(GENERATED): $(SOURCE)
	$(COMPILE_PROTOBUFS_COMMAND)

$(INIT_PY_FILES_TO_CREATE): $(GENERATED_DIRS)
	touch $(INIT_PY_FILES_TO_CREATE)

$(GENERATED_DIRS): $(COSMOS_SDK_DIR) $(WASMD_DIR) $(IBCGO_DIR) $(JUNO_SDK_DIR)

$(COSMOS_SDK_DIR): Makefile
	rm -rfv $(COSMOS_SDK_DIR)
	git clone --branch $(COSMOS_SDK_VERSION) --depth 1 --quiet --no-checkout --filter=blob:none $(COSMOS_SDK_URL) $(COSMOS_SDK_DIR)
	cd $(COSMOS_SDK_DIR) && git checkout $(COSMOS_SDK_VERSION) -- $(COSMOS_PROTO_RELATIVE_DIRS)

$(COSMOS_PROTO_DIR): Makefile
	rm -rfv $(COSMOS_PROTO_DIR)
	git clone --branch $(COSMOS_PROTO_VERSION) --depth 1 --quiet --no-checkout --filter=blob:none $(COSMOS_PROTO_URL) $(COSMOS_PROTO_DIR)
	cd $(COSMOS_PROTO_DIR) && git checkout $(COSMOS_PROTO_VERSION) -- $(COSMOS_PROTO_PROTO_RELATIVE_DIRS)

$(JUNO_SDK_DIR): Makefile
	rm -rfv $(JUNO_SDK_DIR)
	git clone --branch $(JUNO_SDK_VERSION) --depth 1 --quiet --no-checkout --filter=blob:none $(JUNO_SDK_URL) $(JUNO_SDK_DIR)
	cd $(JUNO_SDK_DIR) && git checkout $(JUNO_SDK_VERSION) -- $(JUNO_PROTO_RELATIVE_DIRS)

$(WASMD_DIR): Makefile
	rm -rfv $(WASMD_DIR)
	git clone --branch $(WASMD_VERSION) --depth 1 --quiet --no-checkout --filter=blob:none $(WASMD_URL) $(WASMD_DIR)
	cd $(WASMD_DIR) && git checkout $(WASMD_VERSION) -- $(WASMD_PROTO_RELATIVE_DIRS)

$(IBCGO_DIR): Makefile
	rm -rfv $(IBCGO_DIR)
	git clone --branch $(IBCGO_VERSION) --depth 1 --quiet --no-checkout --filter=blob:none $(IBCGO_URL) $(IBCGO_DIR)
	cd $(IBCGO_DIR) && git checkout $(IBCGO_VERSION) -- $(IBCGO_PROTO_RELATIVE_DIRS)

debug:
	$(info SOURCES_REGEX_TO_EXCLUDE: $(SOURCES_REGEX_TO_EXCLUDE))
	$(info  )
	$(info GENERATED_DIRS: $(GENERATED_DIRS))
	$(info  )
	$(info INIT_PY_FILES_TO_CREATE: $(INIT_PY_FILES_TO_CREATE))
	$(info  )
	$(info SOURCE: $(SOURCE))
	$(info  )
	$(info RELATIVE_SOURCE: $(RELATIVE_SOURCE))
	$(info  )
	$(info GENERATED: $(GENERATED))
	$(info  )
	$(info UNROOTED_SOURCE: $(UNROOTED_SOURCE))
	$(info  )
	$(info PROTO_ROOT_DIRS: $(PROTO_ROOT_DIRS))
	$(info  )
	$(info FIND_CMD: $(FIND_CMD))
	$(info  )
	$(info COMPILE_PROTOBUFS_COMMAND: $(COMPILE_PROTOBUFS_COMMAND))
