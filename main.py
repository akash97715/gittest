df_city_counts = df['city'].value_counts().reset_index().rename(columns={'index': 'city', 'city': 'count'})
