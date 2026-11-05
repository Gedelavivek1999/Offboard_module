#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import select
import termios
import tty

# instructions
msg = """
Control Your Drone with the Keyboard!
----------------um
Moving around:
   w : increase forward velocity
   s : increase backward velocity
   a : increase left velocity
   d : increase right velocity

   q / e : yaw left / yaw right
   space : stop / hover

CTRL-C to quit
"""

class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.settings = termios.tcgetattr(sys.stdin)
        
        self.speed = 0.5  # Linear speed 
        self.turn = 1.0   # Angular speed 
        
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.th = 0.0

        self.get_logger().info("Keyboard Teleop Node Initialized. Use W/A/S/D to move.")
        self.print_instructions()
        
        # publish command (timer->)
        self.timer = self.create_timer(0.1, self.publish_twist)

    def print_instructions(self):
        print(msg)

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def publish_twist(self):
        key = self.get_key()
        if key == 'w':
            self.x = self.speed
        elif key == 's':
            self.x = -self.speed
        elif key == 'a':
            self.y = self.speed
        elif key == 'd':
            self.y = -self.speed
        elif key == 'q':
            self.th = self.turn
        elif key == 'e':
            self.th = -self.turn
        elif key == ' ' or key == 'k':
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
            self.th = 0.0
        elif key == '\x03': 
            rclpy.shutdown()

        twist = Twist()
        twist.linear.x = self.x
        twist.linear.y = self.y
        twist.linear.z = self.z
        twist.angular.z = self.th
        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()
    try:
        rclpy.spin(node)
    except Exception as e:
        print(e)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()