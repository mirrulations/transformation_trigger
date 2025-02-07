# Using Flake8 Locally

## 1. Install Flake8 in a Virtual Environment

To keep your development environment clean, it's recommended to use a virtual environment.

### a. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### b. Once the virtual environment is activated, install flake8 using pip:
```bash 
pip install flake8
```

## 2. Verify Installation

To confirm flake8 is installed correctly, check its version
```bash 
flake8 --version
```

## 3. Running flake8

### a. Check a Single File

```bash
flake8 your_script.py
```

### b. Check Entire Project
Navigate to your project directory and run:

```bash
flake8 .
```

### c. Customize Flake8 Rules

You can ignore or set specific rules using a configuration file (.flake8) in your project root:
Create .flake8 file (We use the parameters below):

```ini
[flake8]
max-line-length = 90
exclude = .git, __pycache__, .venv/*
```

Run flake8 again:

```bash
flake8
```
