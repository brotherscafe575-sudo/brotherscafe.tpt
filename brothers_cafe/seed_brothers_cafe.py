"""
Brothers Cafe — seed script
Run from inside the brothers_cafe folder:
    python seed_brothers_cafe.py
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brothers_cafe.settings')
# Add the project folder to path so Django can find the app
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.management import call_command
call_command('seed_data')
