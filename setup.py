from setuptools import setup, find_packages
import pathlib


readme = pathlib.Path(__file__).parent / "README.md"


setup(name="pnio_dcp",
      use_scm_version={"local_scheme": "no-local-version"},
      setup_requires=['setuptools_scm'],
      description='Discover and configure PROFINET devices with the PROFINET Dynamic Configuration Protocol (DCP) '
                  'protocol.',
      long_description=readme.read_text(encoding='utf-8'),
      long_description_content_type="text/markdown",
      url='https://gitlab.com/pyshacks/pnio_dcp.git',
      author='Dominic Schlagenhof, Katharina Flügel',
      author_email='dominic.schlagenhof@codewerk.de',
      license='MIT © 2020-2021 Codewerk GmbH, Karlsruhe',
      packages=find_packages(),
      install_requires=['psutil', 'setuptools_scm', 'importlib_metadata'],
      extras_require={'test': ['pytest']},
      zip_safe=False)
