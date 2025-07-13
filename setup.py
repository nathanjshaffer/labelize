from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Labelize',
    version='1.1',
    author="Nathan Shaffer",
    author_email="nathanjshaffer@gmail.com",
    description="Gui utility to generate oragnizer labels",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nathanjshaffer/labelize",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'labelize=labelize.run:package',
        ]
    },
    install_requires=[
        'Pint',
        'FreeSimpleGUI',
        'configparser'
    ],
    include_package_data=True,
    package_data={
        "labelize": ["img/labelize.png", "img/help_outline_16dp_1F1F1F.png"],
    },
)
