from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()
    
setup(
    name='PyGNA',
    version='0.8.0',
    description='A python implementation of Generative Network Automata',
    long_description=long_description,
    author='Jeffrey Schmidt',
    author_email='jschmid1@binghamton.edu',
    license = 'BSD',
    url='http://gnaframework.sourceforge.net',
    packages=['PyGNA']
      )
