import os
import logging

from dotenv import load_dotenv

from wandelbots import Instance, MotionGroup
from wandelbots.util.logger import setup_logging

load_dotenv()  # Load environment variables from .env
setup_logging(level=logging.INFO)


my_instance = Instance(
    url=os.getenv("WANDELAPI_BASE_URL"),
    user=os.getenv("NOVA_USERNAME"),
    password=os.getenv("NOVA_PASSWORD"),
)

my_robot = MotionGroup(
    instance=my_instance,
    cell=os.getenv("CELL_ID"),
    motion_group=os.getenv("MOTION_GROUP"),
    default_tcp=os.getenv("TCP"),
)

if __name__ == "__main__":
    
    # Available TCPs on the controller
    print(my_robot.tcps())
    
    # Current joints positions
    print(my_robot.current_joints())
    
    # Current TCP pose
    print(my_robot.current_tcp_pose())
