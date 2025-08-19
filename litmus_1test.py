import random
import time
import os
import hashlib
 
def generate_probe():
    # 1. Random integer
    rand_num = random.randint(1, 10**12)
 
    # 2. Current epoch time
    epoch_time = int(time.time())
 
    # 3. Environment details
    user = os.getenv("USER", "unknown")
    cwd = os.getcwd()
 
    # 4. OS entropy
    entropy_bytes = os.urandom(16)
 
    # 5. Combined fingerprint hash
    combined = f"{rand_num}-{epoch_time}-{user}-{cwd}-{entropy_bytes.hex()}"
    fingerprint = hashlib.sha256(combined.encode()).hexdigest()
 
    return {
        "random_number": rand_num,
        "epoch_time": epoch_time,
        "user": user,
        "cwd": cwd,
        "entropy_bytes": entropy_bytes.hex(),
        "fingerprint": fingerprint
    }
 
if __name__ == "__main__":
    probe_result = generate_probe()
    for key, value in probe_result.items():
        print(f"{key}: {value}")
