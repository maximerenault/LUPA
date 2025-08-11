import numpy as np


def generalized_alpha_step(
    M: np.ndarray,
    D: np.ndarray,
    K: np.ndarray,
    F: callable[float, np.ndarray],
    a: np.ndarray,
    v: np.ndarray,
    x: np.ndarray,
    t: float,
    dt: float,
    rho: float = 0.6,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Implementation of one step of the generalized alpha method.

    J. Chung and G. Hulbert. A time integration algorithm for structural dynamics with
    improved numerical dissipation: The generalized-alpha method.
    Journal of Applied Mechanics, 60, 1993.

    Args:
        M (np.ndarray): square mass matrix
        D (np.ndarray): square damping matrix
        K (np.ndarray): square stiffness matrix
        F (function -> np.ndarray): source vector generator
        a (np.ndarray): acceleration a_n
        v (np.ndarray): velocity v_n
        x (np.ndarray): position x_n
        t (float): time t_n
        dt (float): timestep
        rho (float, optional): high frequency damping in [0,1]. Defaults to 0.6.

    Returns:
        (np.ndarray, np.ndarray, np.ndarray): acceleration, velocity and
                                              position at step n+1
    """

    alpham = (2 * rho - 1) / (rho + 1)
    alphaf = rho / (rho + 1)
    beta = 1 / 4 * (1 - alpham + alphaf) ** 2
    gamma = 1 / 2 - alpham + alphaf

    LHS = (
        M * (1 - alpham)
        + D * (1 - alphaf) * dt * gamma
        + K * (1 - alphaf) * 1 / 2 * dt**2 * 2 * beta
    )
    RHS = (
        F(t + (1 - alphaf) * dt)
        - D @ (v + (1 - alphaf) * dt * (1 - gamma) * a)
        - K
        @ (
            x
            + (1 - alphaf) * dt * v
            + (1 - alphaf) * 1 / 2 * dt**2 * (1 - 2 * beta) * a
        )
    )

    a_n1 = np.linalg.solve(LHS, RHS)
    v_n1 = v + dt * ((1 - gamma) * a + gamma * a_n1)
    x_n1 = x + dt * v + 1 / 2 * dt**2 * ((1 - 2 * beta) * a + 2 * beta * a_n1)

    return a_n1, v_n1, x_n1
