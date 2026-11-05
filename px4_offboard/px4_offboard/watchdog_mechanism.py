import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from px4_msgs.msg import TrajectorySetpoint
from rclpy.clock import Clock

# init watchdog
class CommunicationWatchdog:
    def __init__(self, timeout_duration: float = 1.5):
        self.timeout_duration = timeout_duration
        self.last_cmd_time = Clock().now()
        self.is_timed_out = False

    def feed(self):
        """Kicks the watchdog to reset the timer when a valid message arrives."""
        self.last_cmd_time = Clock().now()
        self.is_timed_out = False

    def check(self, clock: Clock) -> bool:
        """Checks if the elapsed time has exceeded the timeout threshold."""
        elapsed_time = (clock.now() - self.last_cmd_time).nanoseconds / 1e9
        if elapsed_time > self.timeout_duration:
            self.is_timed_out = True
        return self.is_timed_out


class WatchdogTeleopNode(Node):
    def __init__(self):
        super().__init__('watchdog_teleop_node')
        
        self.target_vx = 0.0
        self.target_vy = 0.0

        
        self.watchdog = CommunicationWatchdog(timeout_duration=1.5) #watch dog is set to 1.5 so (1.5->0)
        
        #subsribe
        self.subscription = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10
        )
        self.timer = self.create_timer(0.02, self.deterministic_loop_callback) #determenistic rate_calling
        self.publisher = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10
        )
        self.get_logger().info("Watchdog Mechanism Teleop Node Started.")

    def cmd_vel_callback(self, msg: Twist):
        self.target_vx = msg.linear.x
        self.target_vy = msg.linear.y
        
        self.watchdog.feed()  # feeds on every command

    def deterministic_loop_callback(self):
        
        if self.watchdog.check(self.get_clock()):
            self.target_vx = 0.0
            self.target_vy = 0.0

        # maintains 50 hz  = heartbeart at a time interval of 20ms or 0.02s
        msg = TrajectorySetpoint()
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        msg.velocity = [self.target_vx, self.target_vy, 0.0, 0.0]
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = WatchdogTeleopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()