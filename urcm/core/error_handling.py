
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import replace

from urcm.core.data_models import ResonanceState
from urcm.core.latent_space import SemanticLatentSpace
from urcm.core.attractor_network import AttractorNetwork
from urcm.core.oscillatory_gating import OscillatoryGating
from urcm.core.phoneme_mapper import PhonemeFrequencyMapper

class ErrorRecoverySystem:
    """
    Comprehensive error handling and recovery system for the URCM via mechanism.
    
    Strategies:
    1. Frequency Drift Detection -> Phoneme Region Projection
    2. Semantic Collapse Detection -> Reconstruction Anchoring (Attractor)
    3. Oscillation Desync Detection -> Phase Reset
    """
    
    def __init__(self, 
                 latent_space: SemanticLatentSpace,
                 attractor_network: AttractorNetwork,
                 gating_system: OscillatoryGating,
                 phoneme_mapper: PhonemeFrequencyMapper):
        self.latent_space = latent_space
        self.attractor_network = attractor_network
        self.gating = gating_system
        self.phoneme_mapper = phoneme_mapper
        self.error_log: List[Dict] = []
        
    def check_and_recover(self, state: ResonanceState) -> Tuple[ResonanceState, List[str]]:
        """
        Run all error checks and apply recovery strategies if needed.
        Returns the (possibly corrected) state and a list of actions taken.
        """
        actions = []
        current_state = state
        
        # 1. Semantic Collapse Detection
        # If the vector energy is too low, the signal has lost meaning.
        norm = np.linalg.norm(current_state.resonance_vector)
        if norm < 0.1: # Threshold for collapse
            self._log_error("SemanticCollapse", f"Vector norm {norm:.4f} below threshold")
            
            # Strategy: Anchor to nearest attractor or reset to neutral if none found
            recovered = self._recover_from_collapse(current_state)
            if recovered:
                current_state = recovered
                actions.append("ReconstructionAnchoring")
            else:
                 actions.append("CollapseRecoveryFailed")

        # 2. Frequency Drift Detection
        # We rely on the Latent Space round-trip validation
        # Only check if we haven't already just replaced the whole state
        if "ReconstructionAnchoring" not in actions:
            # Manually perform round trip using SemanticLatentSpace methods
            z = self.latent_space.project(current_state)
            recon_vec = self.latent_space.reconstruct(z)
            _, is_valid = self.latent_space.validate_reconstruction(current_state.resonance_vector, recon_vec)
            
            if not is_valid:
                self._log_error("FrequencyDrift", "Latent space reconstruction failed validation")
                
                # Strategy: Project to nearest valid phoneme region
                current_state = self._project_to_phoneme_region(current_state)
                actions.append("PhonemeRegionProjection")
                
        # 3. Oscillation Desync Detection
        # Check global network coherence (order parameter)
        # Note: This is a system-wide check, but triggered during state processing
        r = self.attractor_network.get_order_parameter()
        if r < 0.3: # Low synchronization
            self._log_error("OscillationDesync", f"Order parameter {r:.4f} < 0.3")
            
            # Strategy: Phase Reset
            self.gating.reset_phase(0.0)
            actions.append("PhaseReset")
            
        return current_state, actions
        
    def _recover_from_collapse(self, state: ResonanceState) -> Optional[ResonanceState]:
        """
        Recover from semantic collapse by anchoring to the nearest stable attractor.
        """
        attractor = self.attractor_network.find_nearest_attractor(phase_threshold=1.0)
        
        if attractor is not None:
            target_dim = state.resonance_vector.shape[0]
            phase_vec = attractor.phase_pattern
            if phase_vec.shape[0] != target_dim:
                resized = np.zeros(target_dim)
                d = min(len(phase_vec), target_dim)
                resized[:d] = phase_vec[:d]
                phase_vec = resized
            norm = np.linalg.norm(phase_vec)
            if norm > 0:
                phase_vec = phase_vec / norm
            return replace(state, resonance_vector=phase_vec, stability_score=0.6, mu_value=0.15)
        
        try:
            neutral_vec = self.phoneme_mapper.map_phoneme('a')
            target_dim = state.resonance_vector.shape[0]
            if neutral_vec.shape[0] != target_dim:
                resized = np.zeros(target_dim)
                d = min(len(neutral_vec), target_dim)
                resized[:d] = neutral_vec[:d]
                neutral_vec = resized
            norm = np.linalg.norm(neutral_vec)
            if norm > 0:
                neutral_vec = neutral_vec / norm
            return replace(state, resonance_vector=neutral_vec, stability_score=0.5, mu_value=0.1)
        except Exception:
            return None

    def _project_to_phoneme_region(self, state: ResonanceState) -> ResonanceState:
        """
        Snap the drifted vector to the nearest valid phoneme vector.
        """
        current_vec = state.resonance_vector
        target_dim = current_vec.shape[0]
        best_dist = float('inf')
        best_vec = current_vec
        
        for phoneme, p_vec in self.phoneme_mapper.phoneme_vectors.items():
            if p_vec.shape[0] != target_dim:
                padded_p = np.zeros(target_dim)
                d = min(len(p_vec), target_dim)
                padded_p[:d] = p_vec[:d]
                target = padded_p
            else:
                target = p_vec
                
            dist = np.linalg.norm(current_vec - target)
            if dist < best_dist:
                best_dist = dist
                best_vec = target
                
        corrected_vec = 0.5 * current_vec + 0.5 * best_vec
        norm = np.linalg.norm(corrected_vec)
        if norm > 0:
            corrected_vec = corrected_vec / norm
            
        return replace(state, resonance_vector=corrected_vec)
        
    def _log_error(self, error_type: str, message: str):
        self.error_log.append({
            "type": error_type,
            "message": message,
            "timestamp": np.datetime64('now')
        })

