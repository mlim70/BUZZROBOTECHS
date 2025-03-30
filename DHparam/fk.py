import numpy as np
import matplotlib.pyplot as plt

def dh_transform(theta_deg, d, a, alpha_deg):
    theta = np.radians(theta_deg)
    alpha = np.radians(alpha_deg)
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha),  np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,              np.sin(alpha),                np.cos(alpha),               d],
        [0,              0,                            0,                           1]
    ])

def forward_kinematics(theta1, theta2, theta3):
    T0 = np.identity(4)
    T1 = T0 @ dh_transform(theta1, 0, 0, 90)
    T2 = T1 @ dh_transform(theta2, 0, 102.72, 0)
    T3 = T2 @ dh_transform(theta3, 0, 145, 0)
    T4 = T3 @ dh_transform(0, 0, 50, 0)

    positions = [T0[:3, 3], T1[:3, 3], T2[:3, 3], T3[:3, 3], T4[:3, 3]]
    return np.array(positions)

def plot_arm(joint_positions):
    xs, ys, zs = joint_positions[:, 0], joint_positions[:, 1], joint_positions[:, 2]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot arm links
    ax.plot(xs, ys, zs, marker='o', linestyle='-', color='blue', linewidth=5)

    # Labels and view
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title("3-DOF Robotic Arm Forward Kinematics")
    ax.set_xlim(-300, 300)
    ax.set_ylim(-300, 300)
    ax.set_zlim(0, 300)
    ax.view_init(elev=30, azim=135)
    plt.show()

# 👉 Enter your joint angles here (in degrees)
theta1 = 45   # Base
theta2 = 45   # Elbow
theta3 = 90   # Wrist

# Compute and plot
joint_positions = forward_kinematics(theta1, theta2, theta3)
plot_arm(joint_positions)
