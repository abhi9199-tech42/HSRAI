import numpy as np
import pytest

from urcm.core.performance import CompressionMonitor, OptimizedPhonemeSet

# ── OptimizedPhonemeSet ─────────────────────────────────────────────

class TestOptimizedPhonemeSet:
    def setup_method(self):
        self.ps = OptimizedPhonemeSet(vector_dimension=24)

    def test_initialization(self):
        assert self.ps.size > 0
        assert self.ps.vector_dimension == 24

    def test_get_phoneme_id_valid(self):
        pid = self.ps.get_phoneme_id("a")
        assert isinstance(pid, int)
        assert pid >= 0

    def test_get_phoneme_id_unknown(self):
        assert self.ps.get_phoneme_id("zzz") is None

    def test_get_phoneme_from_id(self):
        pid = self.ps.get_phoneme_id("a")
        assert self.ps.get_phoneme(pid) == "a"

    def test_get_phoneme_invalid_id(self):
        assert self.ps.get_phoneme(9999) is None

    def test_frequency_vector_shape(self):
        vec = self.ps.get_frequency_vector("a", use_cache=False)
        assert vec.shape == (24,)
        assert vec.dtype == np.float32

    def test_cache_miss_first_access(self):
        self.ps._frequency_cache.clear()
        self.ps._cache_hits = 0
        self.ps._cache_misses = 0
        self.ps.get_frequency_vector("a", use_cache=True)
        assert self.ps._cache_misses == 1
        assert self.ps._cache_hits == 0

    def test_cache_hit_second_access(self):
        self.ps._frequency_cache.clear()
        self.ps._cache_hits = 0
        self.ps._cache_misses = 0
        self.ps.get_frequency_vector("a", use_cache=True)
        self.ps.get_frequency_vector("a", use_cache=True)
        assert self.ps._cache_hits == 1
        assert self.ps._cache_misses == 1

    def test_cache_disabled(self):
        self.ps._frequency_cache.clear()
        self.ps._cache_hits = 0
        self.ps._cache_misses = 0
        self.ps.get_frequency_vector("a", use_cache=False)
        self.ps.get_frequency_vector("a", use_cache=False)
        assert self.ps._cache_hits == 0
        assert self.ps._cache_misses == 2

    def test_cache_stats(self):
        self.ps.get_frequency_vector("a", use_cache=True)
        stats = self.ps.get_cache_stats()
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "hit_rate" in stats
        assert "cache_size" in stats

    def test_memory_usage(self):
        mem = self.ps.get_memory_usage()
        assert mem > 0

    def test_unknown_phoneme_raises(self):
        with pytest.raises(ValueError, match="Unknown phoneme"):
            self.ps.get_frequency_vector("zzz")


# ── CompressionMonitor ──────────────────────────────────────────────

class TestCompressionMonitor:
    def setup_method(self):
        self.monitor = CompressionMonitor()

    def test_initial_empty(self):
        assert self.monitor.get_average_compression_ratio() == 0.0

    def test_record_single(self):
        self.monitor.record_compression(100.0, 50.0)
        assert self.monitor.get_average_compression_ratio() == pytest.approx(2.0)

    def test_record_multiple(self):
        self.monitor.record_compression(100.0, 50.0)
        self.monitor.record_compression(200.0, 40.0)
        avg = self.monitor.get_average_compression_ratio()
        assert avg == pytest.approx(np.mean([2.0, 5.0]))

    def test_efficiency_empty(self):
        eff = self.monitor.get_compression_efficiency()
        assert eff["average_ratio"] == 0.0
        assert eff["meets_threshold"] == False

    def test_efficiency_with_data(self):
        self.monitor.record_compression(100.0, 40.0)
        self.monitor.record_compression(200.0, 80.0)
        eff = self.monitor.get_compression_efficiency()
        assert eff["average_ratio"] == pytest.approx(2.5)
        assert eff["min_ratio"] == pytest.approx(2.5)
        assert eff["max_ratio"] == pytest.approx(2.5)
        assert bool(eff["meets_threshold"]) is True

    def test_validate_efficiency_below_threshold(self):
        self.monitor.record_compression(100.0, 80.0)
        assert bool(self.monitor.validate_efficiency()) is False

    def test_validate_efficiency_above_threshold(self):
        self.monitor.record_compression(100.0, 40.0)
        assert bool(self.monitor.validate_efficiency()) is True

    def test_zero_compressed_size_ignored(self):
        self.monitor.record_compression(100.0, 0.0)
        assert self.monitor.get_average_compression_ratio() == 0.0
