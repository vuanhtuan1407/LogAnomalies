import time

from logger import get_logger
from utils import parse_log_with_datetime

logger = get_logger()


class LogSim:
    def __init__(self, src_path='log_file.log'):
        with open(src_path, 'r') as f:
            self.log_lines = f.readlines()

        self.log_data = parse_log_with_datetime(self.log_lines)

    def stream(self, speed=1.0, delay_epsilon=1.0):
        for i in range(len(self.log_data)):
            dt, content = self.log_data[i]
            logger.info(content)

            if i + 1 < len(self.log_data):
                next_dt = self.log_data[i + 1][0]
                delay = (next_dt - dt).total_seconds() / speed + delay_epsilon
                time.sleep(delay)


if __name__ == "__main__":
    sim = LogSim(src_path='./data/HDFS_v1/HDFS.log')
    sim.stream(delay_epsilon=1e-3)
