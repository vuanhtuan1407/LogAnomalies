from pyflink.table import EnvironmentSettings, TableEnvironment, TableDescriptor, Schema
from pyflink.table.types import DataTypes
from pyflink.table.udf import udf
from pyflink.table.expressions import call, col

env_settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(env_settings)

# create source table
source_schema = Schema.new_builder() \
    .column('value', DataTypes.STRING()) \
    .build()

t_env.create_temporary_table(
    'source',
    TableDescriptor.for_connector('kafka')
    .schema(source_schema)
    .option("topic", "raw_logs")
    .option("properties.bootstrap.servers", "kafka:29092")
    .option("scan.startup.mode", "earliest-offset")
    .format("raw")
    .option("value.format", "raw")
    .option("value.data-type", "STRING")
    .build()
)

# create MinIO sink table
minio_schema = Schema.new_builder() \
    .column('value', DataTypes.STRING()) \
    .build()

t_env.create_temporary_table(
    'minio_sink',
    TableDescriptor.for_connector("filesystem")
    .schema(minio_schema)
    .option("path", "s3a://bucket-cleaned/output/")
    .option("format", "avro")
    .build()
)

# create pg sink table
pg_schema = Schema.new_builder() \
    .column('value', DataTypes.STRING()) \
    .column('label', DataTypes.BOOLEAN()) \
    .build()

t_env.create_temporary_table(
    'pg_sink',
    TableDescriptor.for_connector("jdbc")
    .schema(pg_schema)
    .option("url", "jdbc:postgresql://postgres:5432/system_logs")
    .option("table-name", "inference_results")
    .option("username", "postgres")
    .option("password", "mysecret")
    .option("driver", "org.postgresql.Driver")
    .build()
)


@udf(result_type=DataTypes.ROW([
    DataTypes.FIELD('parsed_log', DataTypes.STRING())
]))
def parse_log(log: str):
    return log


t_env.create_temporary_function('parse_log', parse_log)


@udf(result_type=DataTypes.BOOLEAN())
def predict_anomaly(parsed_log: str):
    return True


t_env.create_temporary_function('predict_anomaly', predict_anomaly)

inp_table = t_env.from_path('source')

parsed = inp_table \
    .select(call('parse_log', col('value')).alias('log')) \
    .select(col('log').get('parsed_log').alias('value'))

parsed.execute_insert('minio_sink').wait()

pred = parsed \
    .select(
    col('value'),
    call('predict_anomaly', col('value')).alias('label')
)

pred.execute_insert('pg_sink').wait()
