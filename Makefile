# Define the Python virtual environment directory
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

# Target to create the virtual environment and install dependencies
setup:
	python3 -m venv $(VENV_DIR)
	$(PIP) install pandas matplot

# Target to run the Python script
run: $(PYTHON)
	$(PYTHON) payback.py
	$(PYTHON) payback_evening_only.py
	$(PYTHON) payback_evening_morning_optional.py
	$(PYTHON) payback_intraday.py

# Clean up the virtual environment
clean:
	rm -rf $(VENV_DIR)
