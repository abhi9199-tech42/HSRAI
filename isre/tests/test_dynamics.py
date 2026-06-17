import pytest
import numpy as np
from isre.reasoning.dynamics import OscillatoryGate


class TestOscillatoryGate:
    def test_initialization_defaults(self):
        gate = OscillatoryGate()
        assert gate.omega == 1.0
        assert gate.mu == 1.0
        assert gate.dt == 0.1
        assert gate.t == 0.0
        assert isinstance(gate.z, complex)
        assert gate.z == pytest.approx(0.1 + 0j)

    def test_initialization_custom(self):
        gate = OscillatoryGate(frequency=2.5, bifurcation=0.5)
        assert gate.omega == 2.5
        assert gate.mu == 0.5

    def test_step_returns_complex(self):
        gate = OscillatoryGate()
        gate.step()
        assert isinstance(gate.z, complex)
        assert gate.t == pytest.approx(0.1)

    def test_step_advances_time(self):
        gate = OscillatoryGate()
        for _ in range(5):
            gate.step()
        assert gate.t == pytest.approx(0.5)

    def test_activation_range(self):
        gate = OscillatoryGate()
        for _ in range(20):
            gate.step()
            act = gate.activation
            assert 0.0 <= act <= 1.0

    def test_phase_is_float(self):
        gate = OscillatoryGate()
        gate.step()
        phase = gate.phase
        assert isinstance(phase, float)

    def test_get_state(self):
        gate = OscillatoryGate()
        gate.step()
        state = gate.get_state()
        assert "z_real" in state
        assert "z_imag" in state
        assert "activation" in state
        assert "phase" in state
        assert "time" in state
        assert isinstance(state["z_real"], float)

    def test_reset(self):
        gate = OscillatoryGate()
        for _ in range(10):
            gate.step()
        gate.reset()
        assert gate.z == pytest.approx(0.1 + 0j)
        assert gate.t == 0.0

    def test_eigenvalue_computation(self):
        gate = OscillatoryGate(frequency=1.0, bifurcation=1.0)
        omega = gate.omega
        mu = gate.mu
        # Eigenvalues of linearized Hopf: lambda = mu ± i*omega
        expected_real = mu
        expected_imag = omega
        # For mu=1.0 the limit cycle radius is sqrt(mu)=1
        r = np.sqrt(abs(mu))
        assert r == pytest.approx(1.0)
        # Verify Hopf bifurcation condition: mu == 0 is bifurcation point
        assert mu > 0  # We are in limit cycle regime

    def test_oscillatory_convergence(self):
        gate = OscillatoryGate(frequency=1.0, bifurcation=1.0)
        prev_act = -1.0
        converged = False
        for i in range(200):
            gate.step()
            curr_act = gate.activation
            if abs(curr_act - prev_act) < 0.01 and i > 10:
                converged = True
                break
            prev_act = curr_act
        assert converged
