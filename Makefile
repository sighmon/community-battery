# Define the Python virtual environment directory
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

# Target to create the virtual environment and install dependencies
setup:
	python3 -m venv $(VENV_DIR)
	$(PIP) install pandas matplotlib

.PHONY: setup run data clean

# Download/cache the configured months and rebuild the combined SA1 data.
data: $(PYTHON)
	PYTHON="$(abspath $(PYTHON))" bash data/download.sh

# Refresh the data, PNGs, and README output in sequence.
run: data
	MPLBACKEND=Agg $(PYTHON) scripts/update_report.py

# Clean up the virtual environment
clean:
	rm -rf $(VENV_DIR)
