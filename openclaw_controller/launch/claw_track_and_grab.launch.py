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
        kinematics_package_path = get_package_share_directory('kinematics')
        openclaw_controller_package_path = get_package_share_directory('openclaw_controller')
    else:
        controller_package_path = '/home/ubuntu/ros2_ws/src/driver/controller'
        kinematics_package_path = '/home/ubuntu/ros2_ws/src/driver/kinematics'
        openclaw_controller_package_path = '/home/ubuntu/ros2_ws/src/openclaw_controller'
        
    # method
    # Track Method color_track (default)  obj_track 
    track_method = LaunchConfiguration('track_method', default='color_track')
    track_method_arg = DeclareLaunchArgument('track_method', default_value=track_method)
    ####################
    kinematics_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(kinematics_package_path, 'launch/kinematics_node.launch.py')),
    )

    claw_track_and_grab_node = Node(
        package='openclaw_controller',
        executable='claw_track_and_grab',
        output='screen',
        parameters=[
            {
                'enable_disp': False,
                'track_method': track_method,
            },
        ],
    )

    return [

            track_method_arg,
            claw_track_and_grab_node,
            kinematics_launch,
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
