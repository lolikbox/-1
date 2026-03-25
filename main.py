#ЗАДАНИЕ ЛР_3 СЕКРЕТНЫЕ КЛЮЧИ 1 часть
import os
my_secret_1=os.environ['MY_SECRET']
my_secret_2=os.environ['MY_SECRET_2']
my_secret_3=os.environ['TAZHIBAEV_1']
my_secret_4=os.environ['TAZHIBAEV_2']

print(my_secret_1,my_secret_2,my_secret_3,my_secret_4)

from sympy import *
import pandas as pd
import matplotlib.pyplot as plt
#2 часть задания (Проверяет Виктор)
##  ИНДИВИДУАЛЬНАЯ ЧАСТЬ ЗАДАНИЯ (3 Вариант)
k, T, C, L = symbols('k T C L')
C_ost = 50000
Am_lst, C_ost_lst = [], []
for i in range(9):
    Am = (C - L) / T #Что это означает?
    # формула расчета платежа # Правильно
    val = float(Am.subs({C: 50000, T: 9, L: 0}))
    C_ost -= val
    Am_lst.append(round(val, 2))
    C_ost_lst.append(round(float(C_ost), 2))
print('Am_lst=', Am_lst)
print('C_ost_lst=', C_ost_lst)
#Все правильно 5, изменилось C_ost = 20000 и T = 6

#2 способ
Aj = 0
C_ost = 50000
Am_lst_2 = []
C_ost_lst_2 = []
for i in range(9):
    Am = k * 1 / T * (C - Aj)
    C_ost -= Am.subs({C: 50000, T: 9, k: 2})
    Am_lst_2.append(round(Am.subs({C: 50000, T: 9, k: 2}), 2))
    Aj += Am
    C_ost_lst_2.append(round(C_ost, 2))
print('Am_lst_2=', Am_lst_2)
print('C_ost_lst_2=', C_ost_lst_2)
#Все правильно 5, изменилось C_ost = 20000 и T = 6



#Табличный вывод
Y = range(1, 7) #Что это означает?
# цикл от 1 о 7  Правильно
table1 = list(zip(Y, C_ost_lst, Am_lst))
table2 = list(zip(Y, C_ost_lst_2, Am_lst_2))
tfame = pd.DataFrame(table1, columns=['Y', 'C_ost_lst', 'Am_lst'])
tfame2 = pd.DataFrame(table2, columns=['Y', 'C_ost_lst_2', 'Am_lst_2'])
print(tfame)
print(tfame2)

#Контейнер визуализации
plt.plot(tfame['Y'], tfame['C_ost_lst'], label='Am')
plt.savefig('chart2_1.png')
plt.figure()
plt.plot(tfame2['Y'], tfame2['C_ost_lst_2'], label='Am2')
plt.savefig('chart2_2.png')
plt.figure()

vals = Am_lst
labels = [str(x) for x in range(1, 10)]
#Все правильно str(x) for x in range(1, 7), 5
explode = (0.1, 0.1, 0.1, 0.1, 0.1, 0.1,0.1,0.1,0.1) #Что это означает? #Список из чисел #Почти правильно
fig, ax = plt.subplots()
ax.pie(vals,
       labels=labels,
       autopct='%1.1f%%',
       shadow=True,
       explode=explode,
       wedgeprops={
           'lw': 1,
           'ls': '--',
           'edgecolor': "k"
       },
       rotatelabels=True)
ax.axis('equal')
plt.savefig('chart2_3.png')
plt.figure()

vals = Am_lst_2
labels = [str(x) for x in range(1, 10)] #Что это означает? #Список из чисел от одного до семи
#Все правильно 5
tt1=20
ее2=40
explode = (0.1, 0.1, 0.1, 0.1, 0.1,0.1, 0.1,0.1, 0.1)
fig, ax = plt.subplots() 
ax.pie(vals,
       explode=explode,
       labels=labels,
       autopct='%1.1f%%',
       shadow=True,
       wedgeprops={
           'lw': 1,
           'ls': '--',
           'edgecolor': "k"
       },
       rotatelabels=True)
ax.axis('equal')
plt.savefig('chart2_4.png')
plt.figure()

plt.figure()
table1 = list(zip(Y, Am_lst))
table2 = list(zip(Y, Am_lst_2))
tfame = pd.DataFrame(table1, columns=['Y', 'Am_lst'])
tfame2 = pd.DataFrame(table2, columns=['Y', 'Am_lst_2'])
plt.bar(tfame['Y'], tfame['Am_lst'])
plt.savefig('chart2_5.png')
plt.figure()
plt.bar(tfame['Y'], tfame2['Am_lst_2'])
plt.savefig('chart2_6.png')
plt.figure()