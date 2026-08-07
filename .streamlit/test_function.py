from erlang_utils import calculate_erlang

print("Imported function")

result = calculate_erlang(
    transactions=100,
    aht=180,
    asa=20,
    interval=1800,
    shrinkage=0.3,
    service_level_target=0.8
)

print(result)
