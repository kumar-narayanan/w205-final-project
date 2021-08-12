#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StructType, StructField, StringType


def all_event_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- desc: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- item: string (nullable = true)
    |-- timestamp: string (nullable = true)
    |-- user_id: string (nullable = true)
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("desc", StringType(), True),
        StructField("item", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("user_id", StringType(), True),
    ])



@udf('boolean')
def is_valid_event(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if (event['event_type'] == 'buy' or event['event_type'] == 'sell' or 
       event['event_type'] == 'play_game' or  event['event_type'] == 'delete'): 
        return True
    return False


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .getOrCreate()

    raw_events = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .load()

    all_events = raw_events \
        .filter(is_valid_event(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          all_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')

    sink = all_events \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_sword_purchases") \
        .option("path", "/tmp/all_events") \
        .trigger(processingTime="10 seconds") \
        .start()

    sink.awaitTermination()


if __name__ == "__main__":
    main()
