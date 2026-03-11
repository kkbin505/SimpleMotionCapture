import matplotlib.pyplot as plt

# Set global styles for a High-Tech Dark Theme
plt.rcParams.update({
    'font.size': 26,
    'text.color': '#E0E0E0',       # Light terminal-like text
    'axes.labelcolor': '#E0E0E0',
    'figure.facecolor': '#0B0E14', # Deep space dark background
    'axes.facecolor': '#0B0E14',
    'savefig.facecolor': '#0B0E14'
})

# Data definition (reflecting your manual edits)
categories = [
    'Engineering', 
    'Prototyping', 
    'Certification', 
    'Operations'
]
amounts = [288000, 50000, 45000, 37000]
total_amount = sum(amounts)

# Labels with white-ish text
labels = [f'{cat}\n(${amt:,})' for cat, amt in zip(categories, amounts)]

# Cyberpunk / Neon Tech Palette
# Using slightly translucent colors for a "glow" feel
colors = ['#00E5FF', '#7000FF', '#FF007A', '#FFD600'] 

# Plotting the donut chart
fig, ax = plt.subplots(figsize=(16, 14))

# Draw the Outer Pie with no edge colors for a seamless look
wedges, texts, autotexts = ax.pie(
    amounts, 
    labels=labels, 
    autopct='%1.0f%%', 
    startangle=90, 
    colors=colors, 
    pctdistance=0.82,
    explode=(0.05, 0, 0, 0),
    wedgeprops={'linewidth': 0, 'edgecolor': 'none', 'alpha': 0.85}
)

# Style text labels manually to ensure they match the dark theme
plt.setp(texts, size=24, weight='bold', color='#B0BEC5')
plt.setp(autotexts, size=26, weight='bold', color='white')

# Create the "Hole" in the middle matching the background
centre_circle = plt.Circle((0,0), 0.65, fc='#0B0E14')
fig.gca().add_artist(centre_circle)

# Add the Total in the center with a "Neon" highlight
plt.text(0, 0, f'TOTAL BUDGET\n${total_amount:,}', 
         ha='center', va='center', 
         fontsize=34, weight='bold', color='#00E5FF')

# Title with high contrast
plt.title('COST DISTRIBUTION', size=40, pad=35, weight='bold', color='white')

# Ensure the pie is a circle
ax.axis('equal')  
plt.tight_layout()

# Save and Show
plt.savefig('development_cost_dark.png', dpi=300, facecolor=fig.get_facecolor())
plt.show()

print("High-tech dark donut chart saved as development_cost_dark.png")