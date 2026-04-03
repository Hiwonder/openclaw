import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription, LaunchService
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    mode = LaunchConfiguration('mode', default='1')
    mode_arg = DeclareLaunchArgument('mode', default_value=mode)
    
    use_asr = LaunchConfiguration('use_asr', default='true')
    use_asr_arg = DeclareLaunchArgument('use_asr', default_value=use_asr)

    tts_node_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('large_models'), 'launch/tts_node.launch.py')
        ),
    )

    vocal_detect_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('large_models'), 'launch/vocal_detect.launch.py')
        ),
        launch_arguments={'mode': mode}.items(),
        condition=IfCondition(use_asr)
    )


    claw_voice = Node(
        package='openclaw_controller',
        executable='claw_voice',
        name='claw_voice',
        output='screen',
        condition=IfCondition(use_asr)
    )
    
    return [
        mode_arg,
        use_asr_arg,
        # tts_node_launch,
        vocal_detect_launch,

        claw_voice,
    ]

def generate_launch_description():
    return LaunchDescription([
        OpaqueFunction(function=launch_setup)
    ])

if __name__ == '__main__':
    ld = generate_launch_description()
    ls = LaunchService()
    ls.include_launch_description(ld)
    ls.run()