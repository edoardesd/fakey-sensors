from numpy import random
import matplotlib.pyplot as plt
import seaborn as sns

sns.distplot(random.normal(loc=18*60, scale=2, size=24*60), hist=False)

plt.show()