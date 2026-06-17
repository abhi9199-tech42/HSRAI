import pytest
import numpy as np

from urcm.core.latent_space import SemanticLatentSpace
from urcm.core.data_models import ResonanceState


def _make_state(input_dim=64):
    rng = np.random.default_rng(10)
    vec = rng.standard_normal(input_dim)
    mu_val = 0.8
    rho = 0.64
    chi = 0.8
    return ResonanceState(
        resonance_vector=vec,
        mu_value=mu_val,
        rho_density=rho,
        chi_cost=chi,
        stability_score=0.9,
        oscillation_phase=1.0,
        timestamp=0.0,
    )


@pytest.fixture
def latent_space():
    return SemanticLatentSpace(input_dim=64, latent_dim=16)


class TestInitialization:
    def test_attributes(self, latent_space):
        assert latent_space.input_dim == 64
        assert latent_space.latent_dim == 16
        assert latent_space.E.shape == (16, 64)
        assert latent_space.D.shape == (64, 16)


class TestProject:
    def test_output_shape(self, latent_space):
        state = _make_state()
        z = latent_space.project(state)
        assert z.shape == (16,)

    def test_invalid_input_dim_raises(self, latent_space):
        state = _make_state(input_dim=32)
        with pytest.raises(ValueError, match="dimension.*mismatch"):
            latent_space.project(state)


class TestReconstruct:
    def test_output_shape(self, latent_space):
        rng = np.random.default_rng(5)
        z = rng.standard_normal(16)
        r = latent_space.reconstruct(z)
        assert r.shape == (64,)

    def test_invalid_latent_dim_raises(self, latent_space):
        bad_z = np.zeros(8)
        with pytest.raises(ValueError, match="dimension.*mismatch"):
            latent_space.reconstruct(bad_z)


class TestRoundTrip:
    def test_low_reconstruction_error(self):
        ls = SemanticLatentSpace(input_dim=64, latent_dim=64)
        state = _make_state()
        z = ls.project(state)
        reconstructed = ls.reconstruct(z)
        error = np.linalg.norm(state.resonance_vector - reconstructed)
        assert error < 0.01

    def test_error_better_than_random(self, latent_space):
        state = _make_state()
        z = latent_space.project(state)
        reconstructed = latent_space.reconstruct(z)
        good_error = np.linalg.norm(state.resonance_vector - reconstructed)

        rng = np.random.default_rng(77)
        random_z = rng.standard_normal(16)
        random_recon = latent_space.reconstruct(random_z)
        bad_error = np.linalg.norm(state.resonance_vector - random_recon)

        assert good_error < bad_error
