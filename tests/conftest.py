import os

# Compiling in the tests never writes a fusion.toml into the repo (Task 31)
os.environ["FUSION_NO_NEW_CONFIG"] = "1"
