import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('MadridZipcodes_Categories.csv', sep=';', index_col=False, header=0)
df.drop(['date', 'Filtered to at 10:42:26'], axis=1, inplace=True)

df2 = df.groupby(["zipcode", "category"]).mean().reset_index(level="category")
df_avgs = df2.loc[df2["category"] == "es_barsandrestaurants"]["avg"].sort_values(ascending=False)
index = df_avgs.index

N = len(df_avgs)
width = 0.5
x = range(N)
plt.bar(x, df_avgs, width, color="#0088cc")
plt.xticks(x, index, rotation='vertical')
plt.title(title)
#plt.show()
plt.savefig('ExampleMatPlotLib.png', bbox_inches='tight')
plt.close()




