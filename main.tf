# ==========================================
# 1. PROVIDER SETUP
# Tells Terraform to use Docker to build infrastructure
# ==========================================
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.0"
    }
  }
}

provider "docker" {
  host = "unix://${pathexpand("~/.docker/desktop/docker.sock")}"
}

# ==========================================
# 2. NETWORKING & STORAGE
# ==========================================

# Create a private network so data warehouse containers can talk to each other safely
resource "docker_network" "data_mesh_net" {
  name = "data_mesh_network"
}

# Create persistent storage for ClickHouse so data survives restarts
resource "docker_volume" "clickhouse_data" {
  name = "clickhouse_data"
}

# Create persistent storage for Metabase dashboards
resource "docker_volume" "metabase_data" {
  name = "metabase_data"
}

# ==========================================
# 3. DOCKER IMAGES
# ==========================================
resource "docker_image" "zookeeper" {
  name         = "confluentinc/cp-zookeeper:7.4.0"
  keep_locally = true
}

resource "docker_image" "kafka" {
  name         = "confluentinc/cp-kafka:7.4.0"
  keep_locally = true
}

resource "docker_image" "clickhouse" {
  name         = "clickhouse/clickhouse-server:latest"
  keep_locally = true
}

resource "docker_image" "metabase" {
  name         = "metabase/metabase:latest"
  keep_locally = true
}

# ==========================================
# 4. CONTAINERS (The Architecture)
# ==========================================

# 4A. Zookeeper (Required to manage Kafka)
resource "docker_container" "zookeeper" {
  name  = "zookeeper"
  image = docker_image.zookeeper.image_id
  networks_advanced {
    name = docker_network.data_mesh_net.name
  }
  env = [
    "ZOOKEEPER_CLIENT_PORT=2181",
    "ZOOKEEPER_TICK_TIME=2000"
  ]
}

# 4B. The Message Queue (Kafka)
resource "docker_container" "kafka" {
  name  = "kafka"
  image = docker_image.kafka.image_id
  networks_advanced {
    name = docker_network.data_mesh_net.name
  }
  depends_on = [docker_container.zookeeper]
  
  # Port 29092 allows local Python script/Hop to push data in
  ports {
    internal = 29092
    external = 29092
  }
  
  env = [
    "KAFKA_BROKER_ID=1",
    "KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181",
    "KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092",
    "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT",
    "KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT",
    "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1"
  ]
}

# 4C. Data Warehouse (ClickHouse)
resource "docker_container" "clickhouse" {
  name  = "clickhouse"
  image = docker_image.clickhouse.image_id
  networks_advanced {
    name = docker_network.data_mesh_net.name
  }
  
  # Port 8123 is the HTTP port (used by Metabase and KNIME)
  ports {
    internal = 8123
    external = 8123
  }
  # Port 9000 is the native client port
  ports {
    internal = 9000
    external = 9000
  }

  env = [
    "CLICKHOUSE_USER=admin",
    "CLICKHOUSE_PASSWORD=admin",
    "CLICKHOUSE_DB=events"
  ]

  # Mount the volume to save the data
  volumes {
    volume_name    = docker_volume.clickhouse_data.name
    container_path = "/var/lib/clickhouse"
  }
}

# 4D. Business Intelligence (Metabase)
resource "docker_container" "metabase" {
  name  = "metabase"
  image = docker_image.metabase.image_id
  networks_advanced {
    name = docker_network.data_mesh_net.name
  }
  
  # Port 3000 for accessing the UI on a  browser
  ports {
    internal = 3000
    external = 3001
  }

  # Mount the volume to save generated dashboards
  volumes {
    volume_name    = docker_volume.metabase_data.name
    container_path = "/metabase-data"
  }
}