import setuptools


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()


setuptools.setup(
    name='icepyus',
    version='2.1',
    author='Omar Ramos Perez',
    author_email='omar.ramos@unison.mx',
    description='Calculo y graficacion de Indices Climaticos ETCCDI.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/OmarRamosPerez/Indices-ETCCDI-precipitacion-/',
    license='GPL-3.0',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=[
        'cdo',
        'numpy',
        'pandas',
        'cartopy',
        'matplotlib',
        'scipy',
        'netCDF4',
    ],
)


