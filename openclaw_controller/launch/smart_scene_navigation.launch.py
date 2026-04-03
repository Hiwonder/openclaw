import os
from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node
from launch_ros.actions import PushRosNamespace
from launch import LaunchDescription, LaunchService
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction, OpaqueFunction, TimerAction, ExecuteProcess
from launch.conditions import IfCondition, LaunchConfigurationEquals
from launch.substitutions import PythonExpression


def launch_setup(context):
    compiled = os.environ['need_compile']
    if compiled == 'True':
        openclaw_controller_package_path = get_package_share_directory('openclaw_controller')
    else:
        openclaw_controller_package_path = '/home/ubuntu/ros2_ws/src/openclaw_controller'


    rosorin_description_package_path = get_package_share_directory('rosorin_description')
    slam_package_path = get_package_share_directory('slam')
    navigation_package_path = get_package_share_directory('navigation')
    large_models_package_path = get_package_share_directory('large_models')
    
    mode = LaunchConfiguration('mode', default=1)
    mode_arg = DeclareLaunchArgument('mode', default_value=mode)
    interruption = LaunchConfiguration('interruption', default=False)
    interruption_arg = DeclareLaunchArgument('interruption', default_value=interruption)

    map_name = LaunchConfiguration('map', default='map_01').perform(context)
    robot_name = LaunchConfiguration('robot_name', default=os.environ['HOST'])
    master_name = LaunchConfiguration('master_name', default=os.environ['MASTER'])

    map_name_arg = DeclareLaunchArgument('map', default_value=map_name)
    master_name_arg = DeclareLaunchArgument('master_name', default_value=master_name)
    robot_name_arg = DeclareLaunchArgument('robot_name', default_value=robot_name)

    use_tts = LaunchConfiguration('use_tts', default='true')
    use_tts_arg = DeclareLaunchArgument('use_tts', default_value=use_tts)
    claw_tts_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(openclaw_controller_package_path, 'launch/include/claw_tts.launch.py')),
        launch_arguments={
            'use_tts': use_tts,
        }.items(),
    )


    camera_topic_value = '/depth_cam/rgb0/image_raw'
    camera_topic = LaunchConfiguration('camera_topic',default=camera_topic_value)
    road_network_map = LaunchConfiguration('road_network_map', default='road_network').perform(context)
    road_network_map_arg = DeclareLaunchArgument('road_network_map', default_value=road_network_map)

    road_network_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('large_models_examples'),
                'large_models_examples/road_network/road_network.launch.py'
            )
        ),
        launch_arguments={
            'camera_topic': camera_topic,
            'file_name': road_network_map,
            'use_yolo_detect': 'false',
        }.items(),
    )


    apriltag_control_node = Node(
        package='openclaw_controller',
        executable='apriltag_control_node',
        output='screen',
        parameters=[
            os.path.join(openclaw_controller_package_path, 'config', 'apriltag_control_roi.yaml'),
            {
                'debug': 'false',
                'enable_display': 'false'
            }
        ]
    )


    navigation_mode = LaunchConfiguration('navigation_mode', default='normal')
    navigation_mode_arg = DeclareLaunchArgument('navigation_mode', default_value=navigation_mode)
    claw_navigation_manager_node = Node(
        package='openclaw_controller',
        executable='claw_navigation_manager',
        output='screen',
        parameters=[
            {
                'navigation_mode': navigation_mode,
            }
        ],
    )


    track_method = LaunchConfiguration('track_method', default='color_track')
    track_method_arg = DeclareLaunchArgument('track_method', default_value=track_method)
    claw_track_and_grab_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(openclaw_controller_package_path, 'launch/claw_track_and_grab.launch.py')),
            launch_arguments={
            'enable_disp': 'false',
            'track_method': track_method,
        }.items(),
    )


    return [
            use_tts_arg,
            map_name_arg, 
            robot_name_arg,
            navigation_mode_arg,
            GroupAction(
                    actions=[
                    claw_tts_launch,
                    claw_navigation_manager_node,
                    road_network_map_arg,
                    road_network_launch,
                    GroupAction(
                        actions=[
                            apriltag_control_node,
                        ],
                        condition=IfCondition(PythonExpression(['"', navigation_mode, '" == "smart_community"']))
                    ),
                    GroupAction(
                        actions=[
                            track_method_arg,
                            claw_track_and_grab_launch,
                        ],
                        condition=IfCondition(PythonExpression(['"', navigation_mode, '" == "smart_factory"']))
                    ),
                ],
            )
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


