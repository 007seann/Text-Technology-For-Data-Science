import code

# Load the data
qrel_df, ttds_df = code.load_data('path/to/qrel.csv', 'path/to/ttdssystemresults.csv')

# Calculate the metrics
avg_p10, avg_r50 = code.calculate_metrics(qrel_df, ttds_df)

print(f"Average P@10: {avg_p10}")
print(f"Average R@50: {avg_r50}")
