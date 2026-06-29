from confluent_kafka import Producer
import json
import time
import random
import sys
import uuid
from datetime import datetime

# Helper function enforcing local machine timezone formatting
def get_local_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 1. Transaction Service Schema
def generate_transaction_event():
    return {
        "transaction_id": str(uuid.uuid4()),
        "user_id": random.randint(1000, 9999),
        "amount": round(random.uniform(5.0, 5000.0), 2),
        "transaction_type": random.choice(["deposit", "withdrawal", "transfer"]),
        "status": random.choices(
            population=["success", "pending", "failed"], 
            weights=[0.8, 0.15, 0.05], # Weighted to simulate realistic success rates
            k=1
        )[0],
        "timestamp": get_local_timestamp()
    }

# 2. Auth Service Schema
def generate_auth_event():
    return {
        "event_id": str(uuid.uuid4()),
        "user_id": random.randint(1000, 9999),
        "action": random.choices(
            population=["login", "logout", "failed_attempt"],
            weights=[0.6, 0.3, 0.1],
            k=1
        )[0],
        "device_os": random.choice(["Android", "iOS", "Web"]),
        "timestamp": get_local_timestamp()
    }

# 3. Goals & Categories Service Schema
def generate_goal_event():
    return {
        "goal_id": str(uuid.uuid4()),
        "user_id": random.randint(1000, 9999),
        "target_amount": round(random.uniform(500.0, 100000.0), 2),
        "category": random.choice(["vacation", "emergency", "savings", "education"]),
        "action": random.choices(
            population=["created", "updated", "completed"],
            weights=[0.5, 0.4, 0.1],
            k=1
        )[0],
        "timestamp": get_local_timestamp()
    }

# 4. Configure the Kafka Producer
# Ensure 'localhost:9092' matches your Docker port mapping for the broker
conf = {
    'bootstrap.servers': 'localhost:29092',
    'client.id': 'multiplexed-python-producer'
}
producer = Producer(conf)

# 5. Delivery Callback function
def delivery_report(err, msg):
    """
    Called exactly once for every message produced to indicate the delivery result.
    """
    if err is not None:
        pass
        # print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        pass
        # Optional: Comment this print statement out if the terminal gets too noisy 
        # at high EPS (Events Per Second)
        # print(f"Successfully delivered to {msg.topic()} [{msg.partition()}]")

# 6. The Iterative Multiplexing Loop
def run_multiplexed_simulation():
    print("Starting iterative multiplexed simulation... Press Ctrl+C to stop.")
    try:
        count = 0
        while True:
            # Domain A: Generate & Send Transaction Event
            txn_payload = generate_transaction_event()
            producer.produce(
                topic='transaction_events',
                value=json.dumps(txn_payload).encode('utf-8'),
                callback=delivery_report
            )

            # Domain B: Generate & Send Auth Event
            auth_payload = generate_auth_event()
            producer.produce(
                topic='auth_events',
                value=json.dumps(auth_payload).encode('utf-8'),
                callback=delivery_report
            )

            # Domain C: Generate & Send Goal Event
            goal_payload = generate_goal_event()
            producer.produce(
                topic='goal_events',
                value=json.dumps(goal_payload).encode('utf-8'),
                callback=delivery_report
            )

            count += 1
            if count % 10000 == 0:
                # Force the message out immediately
                producer.poll(0)
                
            # Pause for a random amount of time to simulate real user traffic(): 1000 to 100,000 Events Per Second
            #time.sleep(0.00001)

    except KeyboardInterrupt:
        print("\nTermination signal received. Initiating graceful drain...")
    finally:
        # Ensure all buffered messages are flushed to Kafka before the script dies
        print("Flushing remaining messages to broker...")
        producer.flush()
        print("Shutdown complete.")

if __name__ == '__main__':
    run_multiplexed_simulation()