from setuptools import setup, find_packages

setup(name='syntactic_structure',
      version='0.1',
      description='Library for syntactic inference and generation',
      author='Minh Pham',
      author_email='minhpham@usc.edu',
      license='MIT',
      packages=find_packages("src"),
      package_dir={'': 'src'},
      zip_safe=False)