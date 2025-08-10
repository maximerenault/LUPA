import numpy as np
import matplotlib.pyplot as plt

R0 = 10
C = 10
R1 = 10

dt = 0.01
tend = 100
time = np.linspace(0, tend, int(tend / dt) + 1, endpoint=True)
Psource = np.sin

solution = np.zeros((4, len(time)))

M0 = np.array(
    [
        [-1, -R0, 0, 0],
        [0, 0, 1, 0],
        [1, 0, 0, -R1],
        [0, 1, -1, -1],
    ]
)

M1 = np.array(
    [
        [0, 0, 0, 0],
        [-C, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
)


def Source(t: float):
    return np.array(
        [
            -Psource(t),
            0,
            0,
            0,
        ]
    )


LHS = M0 + M1 / dt

solution[:, 0] = np.linalg.solve(M0, Source(0))

for step, t in enumerate(time):
    RHS = Source(t) + np.matmul(M1, solution[:, step] / dt)
    try:
        solution[:, step + 1] = np.linalg.solve(LHS, RHS)
    except:
        print("Error: could not solve the system.")
        break

# plt.plot(time, Psource(time), label="PSource")
plt.plot(time, solution.T, label=["P", "Q0", "Q1", "Q2"])
plt.legend()
plt.show()
