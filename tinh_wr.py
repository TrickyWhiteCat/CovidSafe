with open("result.txt", "r") as res_file:
    res = [int(val) for val in res_file.readlines()]

print(f"Winrate: {sum(res)/len(res):.2%}")