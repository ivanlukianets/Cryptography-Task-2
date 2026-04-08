def generate_strumok_relations(n_rounds=11, filename="strumok_11_ticks.txt"):
    with open(filename, "w") as f:
        f.write(f"# Strumok-512 {n_rounds} Rounds\n")
        f.write("connection relations\n")

        for t in range(n_rounds):
            f.write(f"S_{t + 16}, S_{t + 13}, S_{t + 11}, S_{t}\n")
            f.write(f"S_{t + 15}, R1_{t}, R2_{t}, S_{t}\n")
            f.write(f"R1_{t + 1}, R2_{t}, S_{t + 13}\n")
            f.write(f"R2_{t + 1}, R1_{t}\n")

        f.write("end\n")

if __name__ == '__main__':
    generate_strumok_relations(11)