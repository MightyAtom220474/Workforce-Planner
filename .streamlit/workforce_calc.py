# from pyworkforce import ErlangC

# erlang = ErlangC(
#     arrival_rate=100,      # calls per interval
#     service_rate=1/180,    # calls per second (1 / AHT in seconds)
#     agents=12              # number of agents
# )

# service_level = erlang.service_level(target_answer_time=20)  # seconds
# occupancy = erlang.occupancy()
# asa = erlang.asa()

# from pyworkforce import ErlangC 
# import inspect

# print(inspect.signature(ErlangC))

from pyworkforce.queuing import ErlangC

erlang = ErlangC(
    transactions=100,  # calls received
    aht=180,           # average handle time (seconds)
    asa=20,            # target answer time (seconds)
    interval=1800,     # interval length (seconds)
    shrinkage=0.3      # 30% shrinkage
)

result = erlang.required_positions(service_level=0.8)

print(result)

