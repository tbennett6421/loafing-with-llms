import hashlib
 
# ====== INPUT VALUES FROM AI ======
rand_num = 123456789
epoch_time = 123456789
user = "placeholder"
cwd = "placeholder"
entropy_bytes = "placeholder"
fingerprint = "placeholder"

# ====== RECOMPUTE FINGERPRINT ======
combined = f"{rand_num}-{epoch_time}-{user}-{cwd}-{entropy_bytes}"
expected_fingerprint = hashlib.sha256(combined.encode()).hexdigest()
 
# ====== CHECK ======
if expected_fingerprint == fingerprint:
    print("✅ Fingerprint matches! Output is internally consistent.")
else:
    print("❌ Fingerprint mismatch! Output may not be genuine.")
print("Expected fingerprint:", expected_fingerprint)
