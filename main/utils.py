"""
Utility functions
"""

def str_to_bool(val):
    if not val:
        return False
    falsy = ['0', 'false']
    val = val.lower()
    if val in falsy:
        return False
    else:
        return True