"""This script extracts events from Kafka using Spark and writes them to HDFS"""

import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf

@udf('boolean')
def is_valid_event(event_as_json):
    event = json.loads(event_as_json)
    if event['event_type'] == 'sell' or  event['event_type'] == 'buy' or event['event_type'] == 'play_game' or event['event_type'] == 'delete':
        return True
    return False


def main():
    """main
    """
    spark = SparkSession \
    .builder \
    .appName("ExtractEventsJob") \
    .enableHiveSupport() \
    .getOrCreate()

    raw_events = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()

    all_events = raw_events.select(raw_events.value.cast('string').alias('raw'),raw_events.timestamp.cast('string')).filter(is_valid_event('raw'))

    extracted_all_events = all_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.raw))) \
        .toDF()

    extracted_all_events.printSchema()
    extracted_all_events.show()

    extracted_all_events \
        .write \
        .mode('overwrite') \
        .parquet('/tmp/all_events')

    extracted_all_events.registerTempTable("extracted_all_events")

    spark.sql("""
        create external table all_events
        stored as parquet
        location '/tmp/all_events'
        as
        select * from extracted_all_events
    """)

if __name__ == "__main__":
    main()
