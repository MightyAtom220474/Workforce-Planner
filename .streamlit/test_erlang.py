print("1. Starting")

from pyworkforce.queuing import ErlangC

print("2. ErlangC imported")

erlang = ErlangC(
    transactions=100,
    aht=180,
    asa=20,
    interval=1800,
    shrinkage=0.3,
)

print("3. Erlang object created")

result = erlang.required_positions(
    service_level=0.8
)

print("4. Result:")
print(result)