#pip install confluent-kafka
import json
import time
import random
import uuid
from datetime import datetime, timezone
from confluent_kafka import Producer

# 1. Configuration: Tell Python how to connect to local Docker Kafka
conf = {
    'bootstrap.servers': 'localhost:29092', # The port exposed in main.tf
    'client.id': 'service-a-python'
}

producer = Producer(conf)
topic_name = 'service-a-events'

def delivery_report(err, msg):
    """Callback triggered when a message is successfully delivered or fails."""
    if err is not None:
        print(f"ERROR: Message delivery failed: {err}")
    else:
        print(f"SUCCESS: Event Sent! Topic: {msg.topic()} | Partition: {msg.partition()}")

print(f"Starting Microservice A Simulator...")
print(f"Streaming data to Kafka at localhost:29092. Press Ctrl+C to stop.")
print("-" * 50)

# 2. The Simulation Loop
event_types = ['page_view', 'add_to_cart', 'purchase', 'login', 'click']
platforms = ['web', 'ios', 'android']

try:
    while True:
        # Generate a fake event that mimics what a real microservice would produce
        event_data = {
            "event_id": str(uuid.uuid4()),
            "user_id": random.randint(1000, 9999),
            "event_type": random.choice(event_types),
            "platform": random.choice(platforms),
            "amount": round(random.uniform(5.0, 150.0), 2) if random.random() > 0.7 else 0.0,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')        }

        # Convert the Python dictionary to a JSON string
        json_data = json.dumps(event_data)

        # Send to Kafka
        producer.produce(
            topic=topic_name,
            value=json_data.encode('utf-8'),
            callback=delivery_report
        )
        
        # Force the message out immediately
        producer.poll(0)
        
        # Pause for a random amount of time to simulate real user traffic(): 1000 to 100,000 Events Per Second
        time.sleep(random.uniform(0.00001, 0.001))

except KeyboardInterrupt:
    print("\n Stopping simulator...")
finally:
    # Ensure all messages are delivered before closing
    producer.flush()
    print("Disconnected.")
