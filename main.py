import matplotlib.pyplot as plt
import pandas as pd

file_path = 'bench.csv'

df = pd.read_csv(file_path)
df = df.sort_values(by='method')

plt.figure(figsize=(10, 6))
plt.bar(df['method'], df['ms_per_op'])
plt.xlabel('Samba Method')
plt.ylabel('Milliseconds per Operation')
plt.title('Samba Benchmark Results')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('bench.png')
