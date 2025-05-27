# debug.py

import logic
import config

counter = 1
groups = []

if __name__ == "__main__":
    logic.main_logic(counter, groups, config.step)
    print("ok")
