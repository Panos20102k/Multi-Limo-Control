from setuptools import find_packages, setup
import os
from glob import glob


package_name = 'limo_cruise_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='panos',
    maintainer_email='pk586@cornell.edu',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'transient_controller = limo_cruise_control.transient_controller:main',
            'manager = limo_cruise_control.manager:main',
            'pmp_controller = limo_cruise_control.pmp_controller:main',
            'actuation_filter = limo_cruise_control.actuation_filter:main'
        ],
    },
)
