import sys
import os

current_dir_name = os.path.dirname(os.path.abspath(__file__))
parent_dir_name = os.path.dirname(current_dir_name)
source_dir = os.path.join(parent_dir_name, 'shardlib')

sys.path.append(source_dir)
