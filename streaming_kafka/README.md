# Streaming with Kafka to GCP Data Lake





## Table of Contents

## Overview

### Objectives
- placeholder

### Key Features
- placeholder




## title
**Create API Key**
- select `globabl access` for scope
- input: `kafka_tutorial_cluster-api_key` for description as an identifier

**Creat a topic**
- input: `tutorial_topic` for  `Topic name`
- input `2` for partitions
- click show advanced settings and select `1 day` for retention time

save and create

**Producing messages**
produce a message
messages tab > actions > produce a new message

**Create a dummy connector**
datagen source
- select the topic that was just created: tutorial_topic
- gloval access
contnue
JSON
orders template

1 connectyor size

connector name;
ordersconnector_tutorial
contiue

connector will be provisisoined

pause after to reduce costs

create a new topic called `rides`


# Running Spark and Kafka Clusters on Docker

## Build Required Spark Images 

The details of how to spark-images are build in different layers can be created can be read through 
the blog post written by André Perez on [Medium blog -Towards Data Science](https://towardsdatascience.com/apache-spark-cluster-on-docker-ft-a-juyterlab-interface-418383c95445)

```bash
# Build Spark Images
./build.sh 
```

### 2. Create Docker Network & Volume

```bash
# Create Network
docker network  create kafka-spark-network

# Create Volume
docker volume create --name=hadoop-distributed-file-system
```

### 3. Run Services on Docker
```bash
# Start Docker-Compose (within for kafka and spark folders)
docker compose up -d
```
In depth explanation of [Kafka Listeners](https://www.confluent.io/blog/kafka-listeners-explained/)

Explanation of [Kafka Listeners](https://www.confluent.io/blog/kafka-listeners-explained/)

### 4. Stop Services on Docker
```bash
# Stop Docker-Compose (within for kafka and spark folders)
docker compose down
```

### 5. Helpful Comands
```bash
# Delete all Containers
docker rm -f $(docker ps -a -q)

# Delete all volumes
docker volume rm $(docker volume ls -q)
```


