#!/usr/bin/env python3
import pickle
import hashlib

def make_probe(pickle_path=None):
    # dynamic imports
    os = __import__("os")
    time = __import__("time")
    random = __import__("random")
    hashlib_mod = __import__("hashlib")

    rand_num = random.randint(1, 10**12)
    epoch_time = int(time.time())
    user = os.getenv("USER", "unknown")
    cwd = os.getcwd()
    entropy_bytes = os.urandom(16)
    combined = f"{rand_num}-{epoch_time}-{user}-{cwd}-{entropy_bytes.hex()}"
    fingerprint = hashlib_mod.sha256(combined.encode()).hexdigest()
    pickle_sha1 = None
    if pickle_path:
        with open(pickle_path, "rb") as f:
            pickle_sha1 = hashlib_mod.sha1(f.read()).hexdigest()

    probe = {
        "random_number": rand_num,
        "epoch_time": epoch_time,
        "user": user,
        "cwd": cwd,
        "entropy_bytes": entropy_bytes.hex(),
        "fingerprint": fingerprint,
        "pickle_sha1": pickle_sha1
    }

    for k, v in probe.items():
        print(f"{k}: {v}")

    return probe

def make_probe_wrapper():
    return make_probe("demo.pkl")

class Demo:
    def __reduce__(self):
        return (make_probe_wrapper, ())

# Write pickle
with open("demo.pkl", "wb") as f:
    pickle.dump(Demo(), f)

# Load pickle (executes make_probe_wrapper)
with open("demo.pkl", "rb") as f:
    data = pickle.load(f)

print("\nLoaded object:", data)
