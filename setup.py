from setuptools import setup, find_packages
from codecs import open

# Get the long description from the relevant file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Lang',
    version='0.1',
    description='An imperative language that enables verification and inference of the tightest privacy cost for '
                'sophisticated privacy-preserving algorithms.',
    long_description=long_description,
    url='',
    author='Yuin Wang/Ding Ding/Danfeng Zhang/Daniel Kifer',
    author_email='{yxwang,dkifer,zhang}@cse.psu.edu,dxd437@psu.edu',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Programming Language :: Differential Privacy',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='Programming Language, Differential Privacy',
    packages=find_packages(exclude=['tests']),
    install_requires=['pycparser'],
    extras_require={
        'test': ['pytest-cov', 'pytest', 'coverage'],
    },
    entry_points={
        'console_scripts': [
            'lang=lang.__main__:main',
        ],
    },
)
