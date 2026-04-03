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

    if compiled == 'True':
        controller_package_path = get_package_share_directory('controller')
        openclaw_controller_package_path = get_package_share_directory('openclaw_controller')
    else:
        controller_package_path = '/home/ubuntu/ros2_ws/src/driver/controller'
        openclaw_controller_package_path = '/home/ubuntu/ros2_ws/src/openclaw_controller'

    object_track_debug = LaunchConfiguration('object_track_debug', default=False)
    object_track_debug_arg = DeclareLaunchArgument('object_track_debug', default_value=object_track_debug)
    enable_tracking = LaunchConfiguration('enable_tracking', default=True)
    enable_tracking_arg = DeclareLaunchArgument('enable_tracking', default_value=enable_tracking)
    claw_object_track_node = Node(
        package='openclaw_controller',
        executable='claw_object_track',
        output='screen',
        parameters=[
            {
                'enable_tracking': enable_tracking, 
                'object_track_debug': object_track_debug
            },
        ],
    )


    return [
            enable_tracking_arg,
            object_track_debug_arg,

            claw_object_track_node,

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
