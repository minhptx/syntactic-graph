from setuptools import setup

setup(name='syntactic_structure',
      version='0.1',
      description='Library for syntactic inference and generation',
      author='Minh Pham',
      author_email='minhpham@usc.edu',
      license='MIT',
      packages=['syntactic'],
      package_dir={'syntactic': 'src/syntactic'},
      zip_safe=False)