from strumok_tables import FSM, T_non_lin, mul_alpha, mul_alpha_inv

def lfsr_fwd(s0, s11, s13):
    return (mul_alpha(s0) ^ mul_alpha_inv(s11) ^ s13) & 0xFFFFFFFFFFFFFFFF

def lfsr_bwd(s16, s11, s13):
    return mul_alpha_inv((s16 ^ mul_alpha_inv(s11) ^ s13) & 0xFFFFFFFFFFFFFFFF)

def s15_from_z(z, s0, r1, r2):
    return ((z ^ s0 ^ r2) - r1) & 0xFFFFFFFFFFFFFFFF

def simulate(S, r1, r2):
    S = list(S)
    R1, R2, Z = [r1], [r2], []
    for t in range(11):
        Z.append((FSM(S[t + 15], R1[t], R2[t]) ^ S[t]) & 0xFFFFFFFFFFFFFFFF)
        S.append(lfsr_fwd(S[t], S[t + 11], S[t + 13]))
        R2.append(T_non_lin(R1[t]))
        R1.append((R2[t] + S[t + 13]) & 0xFFFFFFFFFFFFFFFF)
    return S, R1, R2, Z

def recover(S, R1, R2, Z):
    changed = True
    while changed:
        changed = False
        for t in range(11):
            if t in R1 and (t + 1) not in R2:
                R2[t + 1] = T_non_lin(R1[t])
                changed = True

            if t in R2 and (t + 13) in S and (t + 1) not in R1:
                R1[t + 1] = (R2[t] + S[t + 13]) & 0xFFFFFFFFFFFFFFFF
                changed = True

            if (t + 1) in R1 and (t + 13) in S and t not in R2:
                R2[t] = (R1[t + 1] - S[t + 13]) & 0xFFFFFFFFFFFFFFFF
                changed = True

            if t in S and (t + 11) in S and (t + 13) in S and (t + 16) not in S:
                S[t + 16] = lfsr_fwd(S[t], S[t + 11], S[t + 13])
                changed = True

            if (t + 16) in S and (t + 11) in S and (t + 13) in S and t not in S:
                S[t] = lfsr_bwd(S[t + 16], S[t + 11], S[t + 13])
                changed = True

            if t < len(Z) and t in S and t in R1 and t in R2 and (t + 15) not in S:
                S[t + 15] = s15_from_z(Z[t], S[t], R1[t], R2[t])
                changed = True

            if t < len(Z) and t in S and (t + 15) in S and t in R2 and t not in R1:
                R1[t] = ((Z[t] ^ S[t] ^ R2[t]) - S[t + 15]) & 0xFFFFFFFFFFFFFFFF
                changed = True

            if t < len(Z) and t in S and (t + 15) in S and t in R1 and t not in R2:
                R2[t] = ((S[t + 15] + R1[t]) ^ Z[t] ^ S[t]) & 0xFFFFFFFFFFFFFFFF
                changed = True

print("###########################################")
print("  Strumok-512: partial guessing attack")
print("  Autoguess basis: 7 words")
print("###########################################")

s = [
    0xAAAAAAAAAAAAAAAA, 0xBBBBBBBBBBBBBBBB,
    0xCCCCCCCCCCCCCCCC, 0xDDDDDDDDDDDDDDDD,
    0xEEEEEEEEEEEEEEEE, 0xFFFFFFFFFFFFFFFF,
    0x1111111111111111, 0x2222222222222222,
    0x3333333333333333, 0x4444444444444444,
    0x5555555555555555, 0x6666666666666666,
    0x7777777777777777, 0x8888888888888888,
    0x9999999999999999, 0x0000000000000000,
]
r1_0, r2_0 = 0, 0
S_ref, R1_ref, R2_ref, Z_ref = simulate(s, r1_0, r2_0)

print("\nWords known to the attacker:")
for t, z in enumerate(Z_ref):
    print(f"    z_{t} = {z}")

print("\nGuessed 7 words:")
BASIS = [2, 6, 10, 11, 12, 13, 14]
for i in BASIS:
    print(f"    S_{i} = {S_ref[i]}")

S_rec  = {i: S_ref[i] for i in BASIS}
R1_rec = {0: r1_0}
R2_rec = {0: r2_0}

recover(S_rec, R1_rec, R2_rec, Z_ref)

print("\nCheck of recovered state:")
errors = 0
for t in range(len(S_ref)):
    got, exp = S_rec.get(t), S_ref[t]
    ok = got == exp
    if not ok:
        errors += 1
    val = f"{got}" if got is not None else "not recovered"
    print(f"    [{'YES' if ok else 'NO'}] S_{t} = {val}" + ("" if ok else f"  (expected {exp})"))

for t in range(len(R1_ref)):
    got, exp = R1_rec.get(t), R1_ref[t]
    ok = got == exp
    if not ok:
        errors += 1
    val = f"{got}" if got is not None else "not recovered"
    print(f"    [{'YES' if ok else 'NO'}] R1_{t} = {val}" + ("" if ok else f"  (expected {exp})"))

for t in range(len(R2_ref)):
    got, exp = R2_rec.get(t), R2_ref[t]
    ok = got == exp
    if not ok:
        errors += 1
    val = f"{got}" if got is not None else "not recovered"
    print(f"    [{'YES' if ok else 'NO'}] R2_{t} = {val}" + ("" if ok else f"  (expected {exp})"))

print("########################################################################################")
print(f"  Result: {'Entire state recovered!' if errors == 0 else f'Errors: {errors}'}")