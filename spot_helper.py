import json
import sys
import time
import bosdyn.client
import bosdyn.client.util
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient
from bosdyn.client import ResponseError, RpcError, create_standard_sdk
from bosdyn.client.lease import LeaseClient, LeaseKeepAlive
from bosdyn.client.lease import Error as LeaseBaseError
from bosdyn.client.estop import EstopClient, EstopEndpoint, EstopKeepAlive
from bosdyn.api import robot_command_pb2 as spot_command_pb2
from bosdyn.client.frame_helpers import BODY_FRAME_NAME
from bosdyn.api import basic_command_pb2
from bosdyn.geometry import EulerZXY
from bosdyn.api.spot import robot_command_pb2 as spot_command_pb2
from bosdyn.api import arm_command_pb2, geometry_pb2, robot_command_pb2, synchronized_command_pb2

VELOCITY_CMD_DURATION = 0.5  # seconds

class SpotRobotController:
    def __init__(self, config_path):
        self.client_name = 'SpotRobotController'
        self.config_path = config_path
        self.hostname = self._load_config()['hostname']
        self.robot = None
        self.command_client = None
        self.lease_client = None
        self.lease_keep_alive = None
        self.estop_client = None
        self.estop_keepalive = None
        self.stop_requested = False  # Ensure this attribute is defined


    def _load_config(self):
        with open(self.config_path, 'r') as config_file:
            config = json.load(config_file)
        return config

    def initialize_robot(self):
        sdk = bosdyn.client.create_standard_sdk(self.client_name)
        self.robot = sdk.create_robot(self.hostname)
        bosdyn.client.util.authenticate(self.robot)
        self.robot.time_sync.wait_for_sync()
        self.command_client = self.robot.ensure_client(RobotCommandClient.default_service_name)
        self.lease_client = self.robot.ensure_client(LeaseClient.default_service_name)
        self.estop_client = self.robot.ensure_client(EstopClient.default_service_name)
        self._robot_command_client = self.robot.ensure_client(RobotCommandClient.default_service_name)


    def acquire_resources(self):
        # Acquire lease
        self.lease = self.lease_client.acquire()
        self.lease_keep_alive = LeaseKeepAlive(self.lease_client)

        # Setup Estop
        self.estop_endpoint = EstopEndpoint(self.estop_client, 'estop', estop_timeout=9.0)
        self.estop_endpoint.force_simple_setup()
        self.estop_keepalive = EstopKeepAlive(self.estop_endpoint)

    def power_on_robot(self):
        if not self.robot.is_powered_on():
            print("Powering on...")
            self.robot.power_on(timeout_sec=20)
            print("Robot powered on.")
        else:
            print("Robot already powered on.")
        
    # Method to set the stop_requested flag
    def request_stop(self):
        self.stop_requested = True

    def toggle_estop(self, engage):
        """Toggle the E-Stop state.

        Args:
            engage (bool): If True, engage the E-Stop. If False, disengage it.
        """
        if engage:
            # Engage E-Stop
            if not self.estop_keepalive:
                self.estop_endpoint = EstopEndpoint(self.estop_client, 'estop', estop_timeout=9.0)
                self.estop_endpoint.force_simple_setup()
                self.estop_keepalive = EstopKeepAlive(self.estop_endpoint)
                print("E-Stop engaged.")
            else:
                print("E-Stop already engaged.")
        else:
            # Disengage E-Stop
            if self.estop_keepalive:
                self.estop_keepalive.stop()
                self.estop_keepalive.shutdown()
                self.estop_keepalive = None
                print("E-Stop disengaged.")
            else:
                print("E-Stop is not engaged.")

    def stand(self):
        if self.stop_requested: return
        print("Commanding robot to stand...")
        cmd = RobotCommandBuilder.synchro_stand_command()
        self.command_client.robot_command(cmd)

    def sit(self):
        if self.stop_requested: return
        print("Commanding robot to sit...")
        cmd = RobotCommandBuilder.synchro_sit_command()
        self.command_client.robot_command(cmd)

    def move(self, velocity_x, velocity_y, velocity_rot, duration=1):
        if self.stop_requested: return
        print(f"Moving: vx={velocity_x}, vy={velocity_y}, vrot={velocity_rot}")
        # Updated command to use synchro_velocity_command
        cmd = RobotCommandBuilder.synchro_velocity_command(velocity_x, velocity_y, velocity_rot)
        end_time_secs = time.time() + duration
        self.command_client.robot_command(cmd, end_time_secs=end_time_secs)


    def move_direction(self, direction, duration):
        if self.stop_requested: return
        """Move the robot in a specified direction for a duration.

        Args:
            direction (str): The direction to move ("forward", "backward", "left", "right").
            duration (float): How long to move in seconds.
        """
        velocity_x = 0
        velocity_y = 0
        if direction == "forward":
            velocity_x = 0.5
        elif direction == "backward":
            velocity_x = -0.5
        elif direction == "left":
            velocity_y = 0.5
        elif direction == "right":
            velocity_y = -0.5
        else:
            print(f"Unknown direction: {direction}")
            return
        self.move(velocity_x, velocity_y, 0, duration)

    def battery_position(self):
        if self.stop_requested: return
        """Commands the robot to assume a position that facilitates battery changing."""
        print("Assuming battery change position...")
        # Using the dir_hint to specify the direction the robot should roll to for battery change
        cmd = RobotCommandBuilder.battery_change_pose_command(
            dir_hint=basic_command_pb2.BatteryChangePoseCommand.Request.HINT_RIGHT)
        self.command_client.robot_command(cmd)


    def rotate(self, direction, duration):
        if self.stop_requested: return
        """Rotate the robot in place.

        Args:
            direction (str): The direction to rotate ("left", "right").
            duration (float): How long to rotate in seconds.
        """
        velocity_rot = 0
        if direction == "left":
            velocity_rot = 0.8  # Rotate left
        elif direction == "right":
            velocity_rot = -0.8  # Rotate right
        else:
            print(f"Unknown direction: {direction}")
            return
        self.move(0, 0, velocity_rot, duration)

    # def crawl(self):
    #    if self.stop_requested: return
    #    """Sets the robot in Crawl mode."""
    #    print("Setting robot to Crawl mode...")
    #    mobility_params = spot_command_pb2.MobilityParams(
    #        locomotion_hint=spot_command_pb2.HINT_CRAWL, stair_hint=0)

    #    cmd = RobotCommandBuilder.synchro_stand_command(params=mobility_params)
    #    self.command_client.robot_command(cmd)


    # Currently not working
    #def hop(self):
    #    print("Attempting to command the robot to hop...")
    #    mobility_params = spot_command_pb2.MobilityParams(
    #        locomotion_hint=spot_command_pb2.HINT_HOP)
    #    cmd = RobotCommandBuilder.synchro_stand_command(params=mobility_params)
    #    # Debug: Print the command to verify its structure
    #    print("Sending command:", cmd)
    #    response = self.command_client.robot_command(cmd)
    #    # Debug: Print the response to see if there are errors or not
    #    print("Command response:", response)

    def self_right(self):
        if self.stop_requested: return
        """Commands the robot to self-right."""
        print("Attempting to self-right...")
        cmd = RobotCommandBuilder.selfright_command()
        self.command_client.robot_command(cmd)

    #def amble(self): Currently not working
    #    """Sets the robot to amble mode."""
    #    print("Setting robot to Amble mode...")
    #    mobility_params = spot_command_pb2.MobilityParams(
    #        locomotion_hint=spot_command_pb2.HINT_AMBLE)
    #    cmd = RobotCommandBuilder.synchro_stand_command(params=mobility_params)
    #    self.command_client.robot_command(cmd)

    def turn_body_pitch_yaw(self, pitch, yaw):
        if self.stop_requested: return
        """Turns the robot's body in pitch and yaw.

        Args:
            pitch (float): The pitch angle in radians.
            yaw (float): The yaw angle in radians.
        """
        print(f"Turning body: pitch={pitch}, yaw={yaw}")
        orientation = EulerZXY(yaw, 0, pitch)  # Yaw, Roll (unused here), Pitch
        cmd = RobotCommandBuilder.synchro_stand_command(footprint_R_body=orientation)
        self.command_client.robot_command(cmd)

    def release_resources(self):
        if self.lease_keep_alive:
            self.sit()
            time.sleep(5)
            self.lease_keep_alive.shutdown()
        if self.estop_keepalive:
            self.sit()
            time.sleep(2)
        self.lease_client.return_lease(self.lease)

    #def arm_cylindrical_velocity_cmd(self, v_r=0.0, v_theta=0.0, v_z=0.0):
    #    """Helper function to build an arm velocity command from unitless cylindrical coordinates."""
    #    cmd = RobotCommandBuilder.arm_velocity_command(v_r, v_theta, v_z)
    #    self.command_client.robot_command(cmd, end_time_secs=time.time() + 0.5)

    def arm_angular_velocity_cmd(self, v_rx=0.0, v_ry=0.0, v_rz=0.0):
        """Helper function to build an arm velocity command from angular velocities."""
        cmd = RobotCommandBuilder.arm_angular_velocity_command(v_rx, v_ry, v_rz)
        self.command_client.robot_command(cmd, end_time_secs=time.time() + 0.5)

    def _arm_cylindrical_velocity_cmd_helper(self, desc='', v_r=0.0, v_theta=0.0, v_z=0.0):
        """ Helper function to build an arm velocity command from unitless cylindrical coordinates."""
        cylindrical_velocity = arm_command_pb2.ArmVelocityCommand.CylindricalVelocity()
        cylindrical_velocity.linear_velocity.r = v_r
        cylindrical_velocity.linear_velocity.theta = v_theta
        cylindrical_velocity.linear_velocity.z = v_z

        arm_velocity_command = arm_command_pb2.ArmVelocityCommand.Request(
            cylindrical_velocity=cylindrical_velocity,
            end_time=self.robot.time_sync.robot_timestamp_from_local_secs(time.time() + 0.5)
        )

        self._arm_velocity_cmd_helper(arm_velocity_command=arm_velocity_command, desc=desc)

    def _arm_velocity_cmd_helper(self, arm_velocity_command, desc=''):

        # Build synchronized robot command
        robot_command = robot_command_pb2.RobotCommand()
        robot_command.synchronized_command.arm_command.arm_velocity_command.CopyFrom(
            arm_velocity_command)

        self._start_robot_command(desc, robot_command,
                                  end_time_secs=time.time() + VELOCITY_CMD_DURATION)

    def _start_robot_command(self, desc, command_proto, end_time_secs=None):

        def _start_command():
            self._robot_command_client.robot_command(command=command_proto,
                                                     end_time_secs=end_time_secs)

        self._try_grpc(desc, _start_command)

    def _try_grpc(self, desc, thunk):
        try:
            return thunk()
        except (ResponseError, RpcError, LeaseBaseError) as err:
            self.add_message(f'Failed {desc}: {err}')
            return None

    def _try_grpc_async(self, desc, thunk):

        def on_future_done(fut):
            try:
                fut.result()
            except (ResponseError, RpcError, LeaseBaseError) as err:
                self.add_message(f'Failed {desc}: {err}')
                return None

        future = thunk()
        future.add_done_callback(on_future_done)

    # Mapping specific movement and rotation commands to the velocity command helpers
    def move_out(self):
        self._arm_cylindrical_velocity_cmd_helper(v_r=0.5)

    def move_in(self):
        self._arm_cylindrical_velocity_cmd_helper(v_r=-0.5)

    def rotate_ccw(self):
        self._arm_cylindrical_velocity_cmd_helper(v_theta=1.0)

    def rotate_cw(self):
        self._arm_cylindrical_velocity_cmd_helper(v_theta=-1.0)

    def move_up(self):
        self._arm_cylindrical_velocity_cmd_helper(v_z=0.5)

    def move_down(self):
        self._arm_cylindrical_velocity_cmd_helper(v_z=-0.5)

    def stow(self):
        """Command to stow the robot's arm."""
        cmd = RobotCommandBuilder.arm_stow_command()
        self.command_client.robot_command(cmd)

    def unstow(self):
        """Command to ready the robot's arm for operation."""
        cmd = RobotCommandBuilder.arm_ready_command()
        self.command_client.robot_command(cmd)