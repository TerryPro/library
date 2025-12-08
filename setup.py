from setuptools import setup, find_packages

setup(
    name="algorithm",
    version="0.1.0",
    description="Algorithm library for JuServer",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        # Add other dependencies if needed
    ],
    python_requires=">=3.8",
)
