import json
import re

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.table import EnvironmentSettings, TableEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer

from postgres.pg import insert_anomaly
from utils import load_templates

TEMPLATES = load_templates()


# Hàm chính để parse từng dòng log
def parse_log_line(line: str):
    """
    Trả về tuple:
    (date, time, pid, level, component, event_id, event_template, template_params)
    """
    log_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2})\s+"  # date
        r"(\d{2}:\d{2}:\d{2})\s+"  # time
        r"(\d+)\s+"  # pid
        r"(\w+)\s+"  # level
        r"([^:]+):\s+"  # component
        r"(.+)"  # content
    )

    match = log_pattern.match(line)
    if not match:
        return None  # dòng log không hợp lệ

    date, time, pid, level, component, content = match.groups()

    # So khớp với các event template
    for event_id, template_str, regex in TEMPLATES:
        match_template = regex.match(content)
        if match_template:
            return (
                date,
                time,
                pid,
                level,
                component,
                event_id,
                template_str,
                json.dumps(match_template.groups())  # serialize các phần match
            )

    # Không khớp template nào
    return (
        date,
        time,
        pid,
        level,
        component,
        "UNKNOWN",
        "",
        json.dumps([])
    )


def main():
    # Khởi tạo Table API environment
    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = TableEnvironment.create(environment_settings=env_settings)

    # 1️⃣ Tạo Kafka Source Table (đọc từ topic 'hdfs-logs')
    t_env.execute_sql("""
        CREATE TABLE kafka_logs (
            raw_line STRING
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'hdfs-logs',
            'properties.bootstrap.servers' = 'kafka:29092',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'raw'  -- raw = không cần format hóa
        )
    """)

    # 2️⃣ Đọc table thành một DataStream (vì cần xử lý tùy biến bằng Python)
    table = t_env.from_path("kafka_logs")
    ds = t_env.to_append_stream(table, type_info=None)  # raw_line là string

    # 3️⃣ Xử lý từng dòng log → match template → ghi PostgreSQL
    (
        ds.map(lambda row: row[0])  # chỉ lấy raw_line
          .map(parse_log_line)
          .filter(lambda r: r is not None and r[5] != "UNKNOWN")
          .map(insert_anomaly)
    )

    # 4️⃣ Kích hoạt thực thi
    t_env.execute("Anomaly Table Job - Kafka → PostgreSQL")


if __name__ == "__main__":
    main()
