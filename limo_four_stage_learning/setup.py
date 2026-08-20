import os
from glob import glob

from setuptools import find_packages, setup


package_name = 'limo_four_stage_learning'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools', 'numpy'],
    zip_safe=True,
    maintainer='panos',
    maintainer_email='pk586@cornell.edu',
    description='Four-stage online Hamiltonian-gradient learning for LIMO cruise control',
    license='Apache-2.0',
    entry_points={'console_scripts': [
        'four_stage_learning = limo_four_stage_learning.learning_node:main',
        'actuation_filter = limo_four_stage_learning.actuation_filter:main',
    ]},
)
