# Define version variables
ARG FLINK_VERSION=1.20.1

# Use the official Flink image as a base image
FROM apache/flink:${FLINK_VERSION}

# Set the working directory inside the container
WORKDIR /opt/flink

# Install curl (for downloading JARs) and pip (for installing PyFlink)
RUN apt-get update && apt-get install -y curl python3-pip

# Install PyFlink using pip
RUN pip3 install apache-flink

# Download the necessary Flink connector JARs using curl into /opt/flink/lib
RUN curl -L https://repo1.maven.org/maven2/org/apache/flink/flink-connector-filesystem_2.12/${FLINK_VERSION}/flink-connector-filesystem_2.12-${FLINK_VERSION}.jar -o /opt/flink/lib/flink-connector-filesystem_2.12-${FLINK_VERSION}.jar \
    && curl -L https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.2.0/flink-connector-jdbc-3.2.0-${FLINK_VERSION}.jar -o /opt/flink/lib/flink-connector-jdbc-3.2.0-${FLINK_VERSION}.jar \
    && curl -L https://repo1.maven.org/maven2/org/apache/flink/flink-s3-fs-hadoop/${FLINK_VERSION}/flink-s3-fs-hadoop-${FLINK_VERSION}.jar -o /opt/flink/lib/flink-s3-fs-hadoop-${FLINK_VERSION}.jar \
    && curl -L https://repo1.maven.org/maven2/org/apache/flink/flink-s3-fs-presto/${FLINK_VERSION}/flink-s3-fs-presto-${FLINK_VERSION}.jar -o /opt/flink/lib/flink-s3-fs-presto-${FLINK_VERSION}.jar \
    && curl -L https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0/flink-sql-connector-kafka-3.3.0-${FLINK_VERSION}.jar -o /opt/flink/lib/flink-sql-connector-kafka-3.3.0-${FLINK_VERSION}.jar

# Copy the custom Flink configuration file into the container
COPY flink-conf.yaml /opt/flink/conf/flink-conf.yaml

# Expose necessary ports
EXPOSE 8081 6121 6122 6123

# Set the entrypoint to run Flink with the JobManager and TaskManager as required
ENTRYPOINT ["/docker-entrypoint.sh"]
