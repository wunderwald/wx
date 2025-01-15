from setuptools import setup, find_packages

setup(
    name='ccf',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'setuptools',
    ],

    author='Moritz Wunderwald',
    author_email='code@moritzwunderwald.de',
    description='ccf - GUI tool for calculating cross-correlation for IBI and EDA data',
    url='https://github.com/yourusername/your-repo',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)