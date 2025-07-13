from setuptools import setup, find_packages

setup(
    name='Labelizer',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'labelizer=labelizer.run:package',
        ]
    },
    install_requires=[
        'Pint',
        'FreeSimpleGUI',
        'configparser'
    ],
    include_package_data=True,
    package_data={
        "labelizer": ["img/labelizer.png", "img/help_outline_16dp_1F1F1F.png"],
    },
)
