#1 способ
from sympy import *
k, T, C, L = symbols('k T C L')
C_ost = 100000
Am_lst, C_ost_lst = [], []
for i in range(5):
    Am = (C - L) / T
    val = float(Am.subs({C: 100000, T: 5, L: 0}))
    C_ost -= val
    Am_lst.append(round(val, 2))
    C_ost_lst.append(round(float(C_ost), 2))
print('Am_lst=', Am_lst)
print('C_ost_lst=', C_ost_lst)

#2 способ
Aj = 0
C_ost = 100000
Am_lst_2 = []
C_ost_lst_2 = []
for i in range(5):
    Am_expr = k * 1 / T * (C - Aj)
    # Вычисляем числовое значение амортизации для текущего года
    Am_val = float(Am_expr.subs({C: 100000, T: 5, k: 2}))
    C_ost -= Am_val
    Am_lst_2.append(round(Am_val, 2))
    # Накапливаем сумму амортизации Aj как число
    Aj += Am_val
    C_ost_lst_2.append(round(float(C_ost), 2))
print('Am_lst_2=', Am_lst_2)
print('C_ost_lst_2=', C_ost_lst_2)

#Табличный вывод
import pandas as pd
Y = list(range(1, 6))
table1 = list(zip(Y, C_ost_lst, Am_lst))
table2 = list(zip(Y, C_ost_lst_2, Am_lst_2))
tfame = pd.DataFrame(table1, columns=['Y', 'C_ost', 'Am_lst'])
tfame2 = pd.DataFrame(table2, columns=['Y', 'C_ost', 'Am_lst_2'])
print(tfame)
print(tfame2)

#Контейнер визуализации
import matplotlib.pyplot as plt

# График 1: Остаточная стоимость (Способ 1)
plt.figure()
plt.plot(tfame['Y'], tfame['C_ost'], label='Остаточная стоимость (1)')
plt.legend()
plt.savefig('chart1.png')

# График 2: Остаточная стоимость (Способ 2)
plt.figure()
plt.plot(tfame2['Y'], tfame2['C_ost'], label='Остаточная стоимость (2)')
plt.legend()
plt.savefig('chart2.png')

# График 3: Пироговая диаграмма амортизации (Способ 1)
vals1 = Am_lst
labels = [str(x) for x in range(1, 6)]
explode = (0.1, 0.1, 0.1, 0.1, 0.1)
fig1, ax1 = plt.subplots()
ax1.pie(vals1, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, 
        wedgeprops={'lw': 1, 'ls': '--', 'edgecolor': "k"}, rotatelabels=True)
ax1.axis('equal')
plt.savefig('chart3.png')

# График 4: Пироговая диаграмма амортизации (Способ 2)
vals2 = Am_lst_2
fig2, ax2 = plt.subplots()
ax2.pie(vals2, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, 
        wedgeprops={'lw': 1, 'ls': '--', 'edgecolor': "k"}, rotatelabels=True)
ax2.axis('equal')
plt.savefig('chart4.png')

# График 5: Столбчатая диаграмма амортизации
plt.figure()
plt.bar(tfame['Y'], tfame['Am_lst'], alpha=0.5, label='Способ 1')
plt.bar(tfame2['Y'], tfame2['Am_lst_2'], alpha=0.5, label='Способ 2')
plt.legend()
plt.savefig('chart5.png')
