import matplotlib.pyplot as plt

# Set global font size for clarity (matching previous request)
plt.rcParams.update({'font.size': 26})

# Cost data
items = [
    'PCBA Service\n($120.00)', 
    'Integration\n($60.00)', 
    'Base Garment\n($45.00)', 
    'Housing\n($30.00)', 
    'IMU Sensors\n($16.80)', 
    'Battery System\n($15.00)', 
    'MCU ESP32\n($3.96)'
]

costs = [120.00, 60.00, 45.00, 30.00, 16.80, 15.00, 3.96]

# Explode the largest part for emphasis
explode = (0.1, 0, 0, 0, 0, 0, 0) 

# Premium color palette
colors = ['#2c3e50', '#2980b9', '#3498db', '#1abc9c', '#27ae60', '#f1c40f', '#e67e22']

# Create the plot
fig, ax = plt.subplots(figsize=(18, 14))

# Plot the pie chart
wedges, texts, autotexts = ax.pie(
    costs, 
    labels=items, 
    autopct='%1.1f%%', 
    startangle=140, 
    colors=colors, 
    explode=explode,
    shadow=True,
    pctdistance=0.85
)

# Style text labels
for text in texts:
    text.set_color('#333333')
    text.set_weight('bold')

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_size(24)

# Draw indicator for a donut chart style if desired (optional, keeping classic for now but cleaner)
# centre_circle = plt.Circle((0,0), 0.70, fc='white')
# fig = plt.gcf()
# fig.gca().add_artist(centre_circle)

# Title
plt.title('Prototype Cost Breakdown (Total: $290.76)', size=36, pad=20, weight='bold')

# Ensure the pie is a circle
ax.axis('equal')  

# Save the plot
plt.tight_layout()
plt.savefig('cost_breakdown_pie.png', dpi=300)
print("Cost breakdown pie chart saved as cost_breakdown_pie.png")
