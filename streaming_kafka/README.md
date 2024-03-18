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
