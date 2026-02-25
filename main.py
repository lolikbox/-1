from sympy import *
k, T, C, L = symbols('k T C L')
C_ost = 100000
Am_lst, C_ost_lst = [], []
for i in range(5):
    Am = (C - L) / T
    # Fixed Cyrillic 'С' to Latin 'C' and ';' to ':'
    val = Am.subs({C: 100000, T: 5, L: 0})
    C_ost -= float(val)
    # Fixed round_two to round and made sure to convert to float for rounding
    Am_lst.append(round(float(val), 2))
    C_ost_lst.append(round(float(C_ost), 2))
print('Am_lst=', Am_lst)
print('C_ost_lst=', C_ost_lst)
