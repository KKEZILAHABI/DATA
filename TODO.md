# Data Mesh PoC: Task Tracker

This document tracks the progress of the local Data Mesh simulation (Hop -> ClickHouse -> Metabase -> KNIME).

## Phase 1: Environment & Setup (Complete)

[x] Install Docker Engine / Podman.

[x] Install Terraform (v1.15.6).

[x] Ensure Apache Hop and KNIME are installed locally.

[x] Initialize Git repository and configure .gitignore.

[x] Update GitHub PAT (Personal Access Token) for remote pushing.

## Phase 2: Infrastructure as Code (Complete)

[x] Write main.tf to define Docker provider.

[x] Configure persistent Docker volumes (clickhouse_data, metabase_data).

[x] Configure isolated Docker network.

[x] Provision Zookeeper and Kafka (Message Queue).

[x] Provision ClickHouse (Data Warehouse).

[x] Provision Metabase on port 3001 (Business Intelligence).

[x] Execute terraform apply successfully.

## Phase 3: Data Ingestion & Streaming (In Progress)

[x] Write Python microservice simulator (service_a_producer.py).

[x] Install confluent_kafka and verify JSON payload delivery to Kafka topic.

[x] Connect to ClickHouse client and create the target service_a_events table.

[x] Open Apache Hop GUI.

[x] Build Hop Pipeline: Consume from Kafka topic (localhost:29092).

[x] Build Hop Pipeline: Parse JSON payload.

[x] Build Hop Pipeline: Bulk insert data into ClickHouse table (localhost:8123).

### Bugs:
[] Timestamp Overshot to 2094

[]  GMT timezome in clickhouse records

[] First Record Changes on Seperate ClickHouse Runs

## Phase 4: Consumption & Analytics (To Do)

[ ] Connect Metabase (localhost:3001) to ClickHouse.

[ ] Create a real-time auto-refreshing dashboard in Metabase for event metrics.

[ ] Connect local KNIME Analytics Platform to ClickHouse via database connector.

[ ] Extract historical data into KNIME and build a sample predictive model / clustering node.

## Phase 5: Operations & Teardown (To Do)

[ ] Document terraform destroy process for clean environment teardown without data loss.

[ ] Verify data persistence upon bringing infrastructure back up.
