import pathlib

from setuptools import setup, find_packages

readme = pathlib.Path(__file__).parent / "README.md"

classifiers = [
                  'Development Status :: 5 - Production/Stable',

                  'Intended Audience :: Developers',
                  'Intended Audience :: Information Technology',
                  'Intended Audience :: System Administrators',
                  'Intended Audience :: Telecommunications Industry',

                  'Topic :: Software Development :: Libraries',
                  'Topic :: Software Development :: Libraries :: Python Modules',
                  'Topic :: System :: Networking',

                  'Operating System :: Microsoft :: Windows',
                  'Operating System :: POSIX :: Linux',

                  'License :: OSI Approved :: MIT License',

                  'Programming Language :: Python :: 3',
                  'Programming Language :: Python :: 3.6',
                  'Programming Language :: Python :: 3.7',
                  'Programming Language :: Python :: 3.8',
                  'Programming Language :: Python :: 3.9',
                  'Programming Language :: Python :: 3.10',
              ]

setup(name="pnio_dcp",
      use_scm_version={"local_scheme": "no-local-version"},
      setup_requires=['setuptools_scm'],
      description='Discover and configure PROFINET devices with the PROFINET Discovery and basic Configuration Protocol (DCP) '
                  'protocol.',
      long_description=readme.read_text(encoding='utf-8'),
      long_description_content_type="text/markdown",
      url='https://gitlab.com/pyshacks/pnio_dcp.git',
      author='Dominic Schlagenhof, Alexander Riedel',
      author_email='dominic.schlagenhof@codewerk.de',
      license='MIT © 2020-2023 Codewerk GmbH, Karlsruhe',
      packages=find_packages(),
      install_requires=['psutil', 'setuptools_scm', 'importlib_metadata'],
      extras_require={'test': ['pytest']},
      python_requires='>=3.6',
      classifiers=classifiers,
      zip_safe=False)
