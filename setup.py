"""
Setup script for the advanced keylogger
"""

from setuptools import setup, find_packages

setup(
    name="advanced_keylogger",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pynput",
        "psutil",
        "pywin32",
    ],
    entry_points={
        'console_scripts': [
            'keylogger=main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced keylogger with command line detection",
    keywords="keylogger, security, monitoring",
    python_requires=">=3.6",
)