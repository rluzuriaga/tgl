from setuptools import setup, find_packages

setup(
    name='tgl',
    version='0.0.2',
    zip_safe=False,
    packages=find_packages(),
    package_data={'tgl': ['data/*.*']},
    entry_points={
        'console_scripts': [
            'tgl = tgl.main:setuptools_entry',
        ],
    },
    install_requires = [
        'requests>=2.23',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
        'Typing :: Typed'
    ]
)
