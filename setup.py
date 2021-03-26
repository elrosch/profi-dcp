from setuptools import setup, find_packages
setup(name="pnio_dcp",
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      description='Structure based on DCP protocol to discover and configure devices in the network',
      url='https://gitlab.com/pyshacks/pnio_dcp.git',
      author='Dominic Schlagenhof, Katharina Flügel',
      author_email='dominic.schlagenhof@codewerk.de',
      license='Copyright (c) 2020-2021 Codewerk GmbH, Karlsruhe.',
      packages=find_packages(),
      install_requires=['psutil', 'setuptools_scm', 'importlib_metadata'],
      zip_safe=False)
