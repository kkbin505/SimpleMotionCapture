import matplotlib.pyplot as plt
import numpy as np

# Set global font size to 26
plt.rcParams.update({'font.size': 26})

# Evaluation categories (English only)
categories = [
    'Accuracy', 
    'Mobility', 
    'Reliability', 
    'Affordability', 
    'Setup Speed', 
    'Data Reliability', 
    'Ecosystem'
]
N = len(categories)

# Scores for each product
# Vision/Kinect (Baseline)
values_kinect = [3, 5, 5, 3, 3, 3, 4]
# Passive Optical (Vicon)
values_vicon = [5, 3, 4, 2, 1, 5, 2]
# IMU-Based (Yours)
values_imu = [4, 5, 4, 5, 5, 5, 5]

# Repeat the first value to close the circular graph
values_kinect += values_kinect[:1]
values_vicon += values_vicon[:1]
values_imu += values_imu[:1]

# Calculate angles for each category
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

# Initialize the plot with polar coordinates
fig, ax = plt.subplots(figsize=(16, 14), subplot_kw=dict(polar=True))

# Draw each product's data
# 1. Vision/Kinect - Increased linewidth to 3
ax.plot(angles, values_kinect, color='#1f77b4', linewidth=3, linestyle='solid', label='Vision/Kinect (Baseline)')
ax.fill(angles, values_kinect, color='#1f77b4', alpha=0.1)

# 2. Passive Optical (Vicon) - Increased linewidth to 3
ax.plot(angles, values_vicon, color='#d62728', linewidth=3, linestyle='solid', label='Passive Optical (Vicon)')
ax.fill(angles, values_vicon, color='#d62728', alpha=0.1)

# 3. IMU-Based (Yours) - Increased linewidth to 4
ax.plot(angles, values_imu, color='#2ca02c', linewidth=4, linestyle='dashdot', label='VR-Suits')
ax.fill(angles, values_imu, color='#2ca02c', alpha=0.2)

# Set theta offset and direction
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

# Set category labels and font size
plt.xticks(angles[:-1], categories, color='black', size=26)

# Set radial ticks and font size
ax.set_rlabel_position(0)
plt.yticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"], color="grey", size=20) # Keeping radial numbers slightly smaller but still large
plt.ylim(0, 5)

# Add legend with font size 20 (26 might be too large for the box)
plt.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=20)

# Set title with font size 26
plt.title('Product Advantage Comparison', size=32, color='#333333', y=1.1)

# Adjust layout and save the high-resolution image
plt.tight_layout()
plt.show()
plt.savefig('comparison_radar_en.png', dpi=300)
print("Updated English radar chart saved as comparison_radar_en.png")
