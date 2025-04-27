#!/usr/bin/env python
"""
Simple script to test that the dashboard template contains the correct marker positioning code
"""
import os
import re

def test_marker_template():
    """Test that the dashboard template contains the correct marker positioning code"""
    template_path = os.path.join('tracking', 'templates', 'tracking', 'dashboard.html')
    
    if not os.path.exists(template_path):
        print(f"ERROR: Template file not found at {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Check for coordinate parsing
    if not re.search(r'const\s+lat\s*=\s*parseFloat\(vehicle\.latitude\)', template_content):
        print("ERROR: Missing latitude parsing code")
        return False
    
    if not re.search(r'const\s+lng\s*=\s*parseFloat\(vehicle\.longitude\)', template_content):
        print("ERROR: Missing longitude parsing code")
        return False
    
    # Check for marker creation with parsed coordinates
    if not re.search(r'L\.marker\(\[lat,\s*lng\]', template_content):
        print("ERROR: Missing marker creation with parsed coordinates")
        return False
    
    # Check for correct icon anchor
    if not re.search(r'iconAnchor:\s*\[\s*20\s*,\s*40\s*\]', template_content):
        print("ERROR: Incorrect icon anchor setting")
        return False
    
    print("SUCCESS: Template contains all the correct marker positioning code")
    return True

if __name__ == '__main__':
    success = test_marker_template()
    exit(0 if success else 1)
