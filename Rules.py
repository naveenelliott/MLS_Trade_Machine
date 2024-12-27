import pandas as pd


# getting the gam for 2025
gam = pd.read_csv('2025 GAM.csv')

# getting the tam for 2025
tam = 2225000

# getting the salary cap for 2025
cap = 5950000

# dp salary budget charge
dp_charge = 743750

players = pd.read_csv('ASA_Players_API.csv')

salaries = pd.read_csv('Salary_Data_ASI.csv')