from setuptools import setup, find_packages


setup(
    name='shiva-deployer',
    version='1.0',
    description='Robust automated deployment for Python projects',
    long_description=open('README.rst').read(),
    author='Erik Rose',
    author_email='erik@mozilla.com',
    license='MIT',
    packages=find_packages(exclude=['ez_setup']),
    entry_points={
        'console_scripts': ['shiva = shiva_deployer.commandline:main']
        },
    url='https://github.com/erikrose/shiva',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration'
        ],
    keywords=['install', 'installation', 'packaging', 'continuous deployment',
              'deploy', 'deployment']
)
