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

    device_base_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(openclaw_controller_package_path, 'launch/include/device_base.launch.py')),
    )

    use_asr = LaunchConfiguration('use_asr', default='false')
    use_asr_arg = DeclareLaunchArgument('use_asr', default_value=use_asr)
    voice_control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(openclaw_controller_package_path, 'launch/include/voice_control.launch.py')),
        launch_arguments={
            'use_asr': use_asr,
        }.items(),
    )

    init_pose_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(controller_package_path, 'launch/init_pose.launch.py')),
        launch_arguments={
            'namespace': '',  
            'use_namespace': 'false',
            'action_name': 'init',
        }.items(),
    )

    claw_move_control_node = Node(
        package='openclaw_controller',
        executable='claw_move_control',
        output='screen',
    )
    claw_arm_group_control_node = Node(
        package='openclaw_controller',
        executable='claw_arm_group_control',
        output='screen',
    )

    use_tts = LaunchConfiguration('use_tts', default='true')
    use_tts_arg = DeclareLaunchArgument('use_tts', default_value=use_tts)
    claw_tts_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(openclaw_controller_package_path, 'launch/include/claw_tts.launch.py')),
        launch_arguments={
            'use_tts': use_tts,
        }.items(),
    )
    
    ####################
    object_track_debug = LaunchConfiguration('object_track_debug', default=False)
    object_track_debug_arg = DeclareLaunchArgument('object_track_debug', default_value=object_track_debug)
    enable_tracking = LaunchConfiguration('enable_tracking', default=True)
    enable_tracking_arg = DeclareLaunchArgument('enable_tracking', default_value=enable_tracking)
    claw_object_track_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(openclaw_controller_package_path, 'launch/claw_object_track.launch.py')),
            launch_arguments={
            'enable_tracking': enable_tracking, 
            'object_track_debug': object_track_debug
        }.items(),  
    )


    ####################
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
            use_asr_arg,
            track_method_arg,
            enable_tracking_arg,
            object_track_debug_arg,
            
            device_base_launch,
            init_pose_launch,

            claw_move_control_node,
            claw_arm_group_control_node,
            claw_tts_launch,

            claw_object_track_launch,

            claw_track_and_grab_launch,
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
