"""
Setup script for Clinic Inventory & Asset Management Module
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="clinic-inventory",
    version="1.0.0",
    author="Clinic Management Team",
    author_email="admin@clinic.com",
    description="Inventory & Asset Management Module for Clinic Management System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clinic/inventory-module",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-django>=4.0",
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
        ],
        "prod": [
            "gunicorn>=20.0",
            "psycopg2-binary>=2.8",
            "redis>=4.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
