import numpy as np
from enum import Enum
from typing import Callable


class TimeIntegration(Enum):
    BDF = "BDF"
    BDF2 = "BDF2"
    BDF3 = "BDF3"


def build_LHS_BDF(D: np.ndarray, K: np.ndarray, dt: float) -> np.ndarray:
    """
    Build left hand side of the equation.

    Args:
        D (np.ndarray): damping matrix
        K (np.ndarray): stiffness matrix
        dt (float): timestep
    Returns:
        np.ndarray: left hand side matrix
    """
    return K + D / dt


def build_LHS_BDF2(D: np.ndarray, K: np.ndarray, dt: float) -> np.ndarray:
    """
    Build left hand side of the equation.

    Args:
        D (np.ndarray): damping matrix
        K (np.ndarray): stiffness matrix
        dt (float): timestep
    Returns:
        np.ndarray: left hand side matrix
    """
    return K + 3 / (2 * dt) * D


def build_LHS_BDF3(D: np.ndarray, K: np.ndarray, dt: float) -> np.ndarray:
    """
    Build left hand side of the equation.

    Args:
        D (np.ndarray): damping matrix
        K (np.ndarray): stiffness matrix
        dt (float): timestep
    Returns:
        np.ndarray: left hand side matrix
    """
    return K + 11 / (6 * dt) * D


def build_RHS_BDF(
    D: np.ndarray,
    F: np.ndarray,
    dt: float,
    step: int,
    x: np.ndarray,
) -> np.ndarray:
    """
    Build right hand side of the equation.

    Args:
        D (np.ndarray): damping matrix
        F (np.ndarray): source vector
        dt (float): timestep
        step (int): current time step
        x (np.ndarray): solution vectors at all steps
    Returns:
        np.ndarray: right hand side vector
    """
    return F + D @ (x[:, step] / dt)


def build_RHS_BDF2(
    D: np.ndarray,
    F: np.ndarray,
    dt: float,
    step: int,
    x: np.ndarray,
) -> np.ndarray:
    """
    Build right hand side of the equation.

    Args:
        D (np.ndarray): damping matrix
        F (np.ndarray): source vector
        dt (float): timestep
        step (int): current time step
        x (np.ndarray): solution vectors at all steps
    Returns:
        np.ndarray: right hand side vector
    """
    return F + D @ ((4 * x[:, step] - x[:, step - 1]) / (2 * dt))


def build_RHS_BDF3(
    D: np.ndarray,
    F: np.ndarray,
    dt: float,
    step: int,
    x: np.ndarray,
) -> np.ndarray:
    """
    Build right hand side of the equation.

    Args:
        D (np.ndarray): damping matrix
        F (np.ndarray): source vector
        dt (float): timestep
        step (int): current time step
        x (np.ndarray): solution vectors at all steps
    Returns:
        np.ndarray: right hand side vector
    """
    return F + D @ (
        (18 * x[:, step] - 9 * x[:, step - 1] + 2 * x[:, step - 2]) / (6 * dt)
    )


def get_system_builders(ti: TimeIntegration) -> tuple[Callable, Callable]:
    """
    Get the appropriate LHS and RHS builders based on the time integration method.

    Args:
        ti (TimeIntegration): Time integration method

    Returns:
        tuple: (LHS builder function, RHS builder function)
    """
    if ti == TimeIntegration.BDF:
        return build_LHS_BDF, build_RHS_BDF
    elif ti == TimeIntegration.BDF2:
        return build_LHS_BDF2, build_RHS_BDF2
    elif ti == TimeIntegration.BDF3:
        return build_LHS_BDF3, build_RHS_BDF3
    else:
        raise ValueError(f"Unknown time integration method: {ti}")


def generalized_alpha_step(
    M: np.ndarray,
    D: np.ndarray,
    K: np.ndarray,
    F: Callable[[float], np.ndarray],
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
        M (np.ndarray): square mass matrix (for a)
        D (np.ndarray): square damping matrix (for v)
        K (np.ndarray): square stiffness matrix (for x)
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
