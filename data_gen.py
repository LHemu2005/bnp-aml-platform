import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid

def generate_aml_data(num_records=2000):
    np.random.seed(42)
    random.seed(42)
    
    # Entities
    normal_users = [f"CUST-{i:04d}" for i in range(1, 101)]
    smurf_nodes = [f"CUST-S-{i}" for i in range(1, 15)]
    crypto_wallets = [f"WALLET-0x{uuid.uuid4().hex[:6].upper()}" for i in range(10)]
    shell_companies = [f"CORP-{i:04d}" for i in range(1, 5)]
    
    ips = [f"192.168.1.{i}" for i in range(1, 50)]
    devices = [f"DEV-DESK-{i}" for i in range(1, 50)]
    
    data = []
    base_time = datetime.now() - timedelta(days=30)
    
    # Normal Transactions
    for _ in range(num_records - 200):
        sender = random.choice(normal_users)
        receiver = random.choice(normal_users + shell_companies)
        if sender == receiver: continue
            
        data.append({
            "transaction_id": f"TXN{random.randint(100000, 999999)}",
            "timestamp": (base_time + timedelta(minutes=random.randint(1, 40000))).isoformat() + "Z",
            "sender_account": sender,
            "sender_name": f"User {sender}",
            "sender_customer_id": sender,
            "receiver_account": receiver,
            "receiver_name": f"Entity {receiver}",
            "receiver_customer_id": receiver,
            "amount": round(random.uniform(100, 50000), 2),
            "currency": "INR",
            "channel": random.choice(["UPI", "NEFT", "RTGS", "IMPS"]),
            "ip_address": random.choice(ips),
            "device_id": random.choice(devices),
            "location_country": "India",
            "location_city": random.choice(["Mumbai", "Delhi", "Bangalore", "Nagpur"]),
            "is_crypto": False,
            "crypto_wallet": ""
        })

    # Scenario 1: Structuring / Smurfing
    # Large amount broken into < 10,000 INR
    master_node = "CUST-MASTER-01"
    for smurf in smurf_nodes[:5]:
        for _ in range(6): # > 5 txns to trigger rule
            data.append({
                "transaction_id": f"TXN{random.randint(100000, 999999)}",
                "timestamp": (base_time + timedelta(minutes=random.randint(1, 1440))).isoformat() + "Z",
                "sender_account": master_node,
                "sender_name": "Master Smurfer",
                "sender_customer_id": master_node,
                "receiver_account": smurf,
                "receiver_name": f"Smurf {smurf}",
                "receiver_customer_id": smurf,
                "amount": round(random.uniform(8000, 9999), 2),
                "currency": "INR",
                "channel": "UPI",
                "ip_address": ips[0],
                "device_id": devices[0],
                "location_country": "India",
                "location_city": "Mumbai",
                "is_crypto": False,
                "crypto_wallet": ""
            })

    # Scenario 2: Circular Money Flow (A -> B -> C -> A)
    circ_nodes = ["CUST-CIRC-A", "CUST-CIRC-B", "CUST-CIRC-C"]
    for i in range(3):
        sender = circ_nodes[i]
        receiver = circ_nodes[(i + 1) % 3]
        data.append({
            "transaction_id": f"TXN{random.randint(100000, 999999)}",
            "timestamp": (base_time + timedelta(hours=i)).isoformat() + "Z",
            "sender_account": sender,
            "sender_name": sender,
            "sender_customer_id": sender,
            "receiver_account": receiver,
            "receiver_name": receiver,
            "receiver_customer_id": receiver,
            "amount": 500000.00,
            "currency": "INR",
            "channel": "RTGS",
            "ip_address": ips[1],
            "device_id": devices[1],
            "location_country": "India",
            "location_city": "Delhi",
            "is_crypto": False,
            "crypto_wallet": ""
        })

    # Scenario 3: Crypto Off-ramping
    crypto_sender = "CUST-SHADY-01"
    wallet = crypto_wallets[0]
    data.append({
        "transaction_id": f"TX-CRYPTO-{random.randint(100000, 999999)}",
        "timestamp": (base_time + timedelta(days=2)).isoformat() + "Z",
        "sender_account": crypto_sender,
        "sender_name": "Shady User",
        "sender_customer_id": crypto_sender,
        "receiver_account": wallet,
        "receiver_name": "Crypto Exchange",
        "receiver_customer_id": "CUST-CRYPTO-EX",
        "amount": 1200000.00,
        "currency": "USDT",
        "channel": "Crypto Gateway",
        "ip_address": ips[2],
        "device_id": devices[2],
        "location_country": "Unknown",
        "location_city": "Offshore",
        "is_crypto": True,
        "crypto_wallet": wallet
    })
    
    df = pd.DataFrame(data)
    df.to_csv("aml_dataset.csv", index=False)
    print("Generated aml_dataset.csv with Hackathon Schema!")

if __name__ == "__main__":
    generate_aml_data()
