import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'openclaw_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ROSOrinPro@example.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'claw_move_control = openclaw_controller.robot_base_control.claw_move_control:main',
            'claw_arm_group_control = openclaw_controller.robot_base_control.claw_arm_group_control:main',

            'claw_object_track = openclaw_controller.claw_object_track.claw_object_track:main',
            'claw_track_and_grab = openclaw_controller.claw_track_and_grab.claw_track_and_grab:main',

            'claw_tts = openclaw_controller.claw_tts:main',
            'claw_voice = openclaw_controller.claw_voice:main',
            
            'claw_navigation_manager = openclaw_controller.navigation_manager.claw_navigation_manager:main',

            'apriltag_control_node = openclaw_controller.apriltag_control_node.apriltag_control_node:main',
        ],
    },
)
