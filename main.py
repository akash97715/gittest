import numpy as np

# Calculate Q1, Q3, and IQR
Q1 = df.quantile(0.25)
Q3 = df.quantile(0.75)
IQR = Q3 - Q1

# Define bounds for outliers
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Replace outliers with median
df = df.apply(lambda x: np.where((x < lower_bound[x.name]) | (x > upper_bound[x.name]), x.median(), x))
