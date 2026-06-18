import cmath
from typing import Any, Dict


class OscillatoryGate:
    """
    Implements Hopf oscillator dynamics for path activation gating.
    Requirement 3.3: Oscillatory gating mechanisms.
    Requirements 7.3: Oscillatory convergence.
    """
    def __init__(self, frequency: float = 1.0, bifurcation: float = 1.0):
        self.z: complex = 0.1 + 0j # Initial state
        self.omega = frequency      # Natural frequency
        self.mu = bifurcation       # Bifurcation parameter (controls limit cycle)
        self.dt = 0.1               # Time step
        self.t = 0.0

    def step(self):
        """
        Evolves the oscillator state by one time step using Euler integration.
        dz/dt = z(mu - |z|^2) + i*omega*z
        """
        r2 = abs(self.z)**2
        dz = self.z * (self.mu - r2) + 1j * self.omega * self.z
        self.z += dz * self.dt
        self.t += self.dt

    @property
    def activation(self) -> float:
        """
        Returns a value between 0 and 1 derived from the oscillator's real part.
        Used to gate reasoning path activity.
        """
        # Map real part to [0, 1] sigmoid-like or just normalized amplitude
        # Simple projection: (Re(z) + 1) / 2 clipped
        val = (self.z.real + 1.0) / 2.0
        return max(0.0, min(1.0, val))

    @property
    def phase(self) -> float:
        return cmath.phase(self.z)

    def get_state(self) -> Dict[str, Any]:
        return {
            "z_real": self.z.real,
            "z_imag": self.z.imag,
            "activation": self.activation,
            "phase": self.phase,
            "time": self.t
        }

    def reset(self):
        self.z = 0.1 + 0j
        self.t = 0.0
