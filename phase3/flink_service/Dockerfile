FROM apache/flink:2.0-scala_2.12

# Install Python as root
USER root

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip netcat-openbsd curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python libraries
COPY requirements.txt /app/
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Create symlink
RUN ln -s /usr/bin/python3 /usr/bin/python

# Download the Kafka connector JAR
RUN curl -o /opt/flink/lib/flink-sql-connector-kafka-4.0.0-2.0.jar \
    https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/4.0.0-2.0/flink-sql-connector-kafka-4.0.0-2.0.jar

# Set Python environment variables
ENV PYFLINK_CLIENT_EXECUTABLE=python
ENV PYFLINK_EXECUTABLE=python
ENV PYTHONPATH=/app

# Copy the job files
COPY . /app

# Switch back to unprivileged user
USER flink  