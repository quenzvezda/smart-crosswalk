import threading

# Global variables
is_minimum_time_reach = False
isProcessRun = False
lock = threading.Lock()

# Setter for is_minimum_time_reach
def set_is_minimum_time_reach(value):
    global is_minimum_time_reach
    is_minimum_time_reach = value

# Getter for is_minimum_time_reach
def get_is_minimum_time_reach():
    global is_minimum_time_reach
    return is_minimum_time_reach
