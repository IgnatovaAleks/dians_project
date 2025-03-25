package com.finance.realtime

import org.apache.kafka.clients.consumer.ConsumerConfig
import org.apache.kafka.common.serialization.StringDeserializer
import org.apache.spark.SparkConf
import org.apache.spark.streaming.kafka010.{ConsumerStrategies, KafkaUtils, LocationStrategies}
import org.apache.spark.streaming.{Seconds, StreamingContext}
import org.apache.spark.sql.{SparkSession, SaveMode}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import com.finance.realtime.models.StockData
import org.json4s._
import org.json4s.jackson.JsonMethods._
import java.sql.Timestamp
import java.time.LocalDateTime

object SparkStreamingApp {

  def main(args: Array[String]): Unit = {
    val conf = new SparkConf()
      .setAppName("Finance Real-Time Processing")
      .setMaster("spark://spark-master:7077")
      .set("spark.executor.memory", "1g")

    val spark = SparkSession.builder()
      .config(conf)
      .getOrCreate()

    import spark.implicits._

    val ssc = new StreamingContext(spark.sparkContext, Seconds(30))
    
    val kafkaParams = Map[String, Object](
      ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG -> "kafka:9092",
      ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG -> classOf[StringDeserializer],
      ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG -> classOf[StringDeserializer],
      ConsumerConfig.GROUP_ID_CONFIG -> "finance-processing-group",
      ConsumerConfig.AUTO_OFFSET_RESET_CONFIG -> "latest",
      ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG -> (false: java.lang.Boolean)
    )
    
    val topics = Array("stock-data")
    
    val stream = KafkaUtils.createDirectStream[String, String](
      ssc,
      LocationStrategies.PreferConsistent,
      ConsumerStrategies.Subscribe[String, String](topics, kafkaParams)
    )
    
    implicit val formats = DefaultFormats
    
    stream.foreachRDD { rdd =>
      if (!rdd.isEmpty()) {
        val stockDataDF = rdd.map(record => {
          val json = parse(record.value())
          val symbol = (json \ "symbol").extract[String]
          val price = (json \ "price").extract[BigDecimal]
          val volume = (json \ "volume").extract[BigDecimal]
          val timestamp = (json \ "timestamp").extract[String]
          val dateTime = LocalDateTime.parse(timestamp)
          val source = (json \ "source").extract[String]
          
          StockData(symbol, price.toDouble, volume.toLong, new Timestamp(dateTime.toEpochSecond(java.time.ZoneOffset.UTC) * 1000), source)
        }).toDF()
        
        stockDataDF.write
          .format("org.apache.spark.sql.cassandra")
          .options(Map("keyspace" -> "finance", "table" -> "raw_stock_data"))
          .mode(SaveMode.Append)
          .save()
          
        val aggregatedDF = stockDataDF
          .groupBy($"symbol", window($"timestamp", "1 hour"))
          .agg(
            avg($"price").as("avg_price"),
            max($"price").as("max_price"),
            min($"price").as("min_price"),
            sum($"volume").as("total_volume")
          )
        
        aggregatedDF.write
          .format("jdbc")
          .option("url", "jdbc:postgresql://postgres:5432/financedb")
          .option("dbtable", "aggregated_stock_data")
          .option("user", "financeuser")
          .option("password", System.getenv("POSTGRES_PASSWORD"))
          .mode(SaveMode.Append)
          .save()
      }
    }
    
    ssc.start()
    ssc.awaitTermination()
  }
}