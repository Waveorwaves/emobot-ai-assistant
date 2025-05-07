"""
Setup script for emobot package.
"""
from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="emobot",
    version="0.1.0",
    description="Personal assistant bot with emotional responses",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'emobot=emobot.main:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)