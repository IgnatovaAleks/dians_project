FROM bitnami/spark:3.3.1

WORKDIR /app

COPY target/finance-realtime-processing.jar /app/finance-realtime-processing.jar

ENV SPARK_MODE=worker
ENV SPARK_MASTER_URL=spark://spark-master:7077
ENV SPARK_RPC_AUTHENTICATION_ENABLED=no
ENV SPARK_RPC_ENCRYPTION_ENABLED=no
ENV SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
ENV SPARK_SSL_ENABLED=no

CMD ["/opt/bitnami/spark/bin/spark-submit", "--master", "spark://spark-master:7077", "--class", "com.finance.realtime.SparkStreamingApp", "/app/finance-realtime-processing.jar"]
