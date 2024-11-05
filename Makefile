# Define the Python virtual environment directory
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

# Target to create the virtual environment and install dependencies
setup:
	python3 -m venv $(VENV_DIR)
	$(PIP) install pandas

# Target to run the Python script
run: $(PYTHON)
	$(PYTHON) payback.py
	$(PYTHON) payback_evening_only.py

# Clean up the virtual environment
clean:
	rm -rf $(VENV_DIR)
