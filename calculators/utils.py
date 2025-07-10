"""
Utility functions for input validation and CLI logic shared across calculators.
"""

def get_float_input(prompt, min_value=None, max_value=None, allow_blank=False, default=None):
    while True:
        try:
            value = input(prompt)
            if allow_blank and value.strip() == "":
                return default
            value = float(value)
            if min_value is not None and value < min_value:
                print(f"Value must be >= {min_value}")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be <= {max_value}")
                continue
            return value
        except ValueError:
            print("Please enter a valid number" if not allow_blank else "Please enter a valid number or leave blank")

def get_int_input(prompt, min_value=None, max_value=None, allow_blank=False, default=None):
    while True:
        try:
            value = input(prompt)
            if allow_blank and value.strip() == "":
                return default
            value = int(value)
            if min_value is not None and value < min_value:
                print(f"Value must be >= {min_value}")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be <= {max_value}")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer" if not allow_blank else "Please enter a valid integer or leave blank")

def get_choice_input(prompt, choices, case_sensitive=False, allow_blank=False, default=None):
    choices_display = "/".join(choices)
    while True:
        value = input(f"{prompt} ({choices_display}): ")
        if allow_blank and value.strip() == "":
            return default
        if not case_sensitive:
            value = value.strip().lower()
            choices = [c.lower() for c in choices]
        if value in choices:
            return value if case_sensitive else choices[[c.lower() for c in choices].index(value)]
        print(f"Please enter one of: {choices_display}") 