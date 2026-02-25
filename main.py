from sympy import *
k, T, C, L = symbols('k T C L')
C_ost = 100000
Am_lst, C_ost_lst = [], []
for i in range(5):
    Am = (C - L) / T
    # Fixed Cyrillic 'С' to Latin 'C' and ';' to ':'
    # Subs values must be floats or ints for rounding
    val = float(Am.subs({C: 100000, T: 5, L: 0}))
    C_ost -= val
    # Replaced round_two with built-in round
    Am_lst.append(round(val, 2))
    C_ost_lst.append(round(float(C_ost), 2))
print('Am_lst=', Am_lst)
print('C_ost_lst=', C_ost_lst)
