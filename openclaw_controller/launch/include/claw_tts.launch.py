



import os
from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch import LaunchDescription, LaunchService
from launch.actions import IncludeLaunchDescription, OpaqueFunction,DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource

def launch_setup(context):
    compiled = os.environ['need_compile']

    tts_node_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('large_models'), 'launch/tts_node.launch.py')
        ),
    )
    use_tts = LaunchConfiguration('use_tts', default='false')
    use_tts_arg = DeclareLaunchArgument('use_tts', default_value=use_tts)
    claw_tts = Node(
        package='openclaw_controller',
        executable='claw_tts',
        name='claw_tts',
        output='screen',
        condition=IfCondition(use_tts)
    )
    return [
        use_tts_arg,
        claw_tts,
        tts_node_launch,
    ]

def generate_launch_description():
    return LaunchDescription([
        OpaqueFunction(function = launch_setup)
    ])

if __name__ == '__main__':
    # 创建一个LaunchDescription对象(create a LaunchDescription object)
    ld = generate_launch_description()

    ls = LaunchService()
    ls.include_launch_description(ld)
    ls.run()
