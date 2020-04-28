from setuptools import setup, find_packages

setup(
    name='TogglCLI',
    version='0.0.1',
    zip_safe=False,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'togglcli = togglcli.main:setuptools_entry',
        ],
    },
    install_requires = [
        'requests>=2.23',
    ]
)