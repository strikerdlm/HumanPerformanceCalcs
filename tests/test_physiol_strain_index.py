"""
Unit tests for PhysiolStrainIndex.py
"""
import pytest
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PhysiolStrainIndex import physiological_strain_index, interpret_psi


class TestPhysiologicalStrainIndex:
    """Test cases for Physiological Strain Index calculation."""
    
    def test_basic_calculation(self):
        """Test basic PSI calculation."""
        # Test case: normal initial values, moderate strain
        psi = physiological_strain_index(37.0, 70, 38.0, 120)
        # Expected PSI should be positive but reasonable
        assert 0 <= psi <= 10
        assert psi > 0  # Should show some strain
    
    def test_no_strain(self):
        """Test PSI calculation with no physiological strain."""
        psi = physiological_strain_index(37.0, 70, 37.0, 70)
        # Should be very low or zero
        assert psi < 1.0
    
    def test_high_strain(self):
        """Test PSI calculation with high physiological strain."""
        psi = physiological_strain_index(37.0, 70, 39.0, 180)
        # Should show high strain
        assert psi > 5.0
        assert psi <= 10.0  # Should be capped at 10
    
    def test_age_adjusted_max_hr(self):
        """Test PSI calculation with age-adjusted max heart rate."""
        psi_young = physiological_strain_index(37.0, 70, 38.0, 150, age=20)
        psi_old = physiological_strain_index(37.0, 70, 38.0, 150, age=60)
        # Older person should show higher strain for same HR
        assert psi_old > psi_young
    
    def test_custom_max_hr(self):
        """Test PSI calculation with custom maximum heart rate."""
        psi = physiological_strain_index(37.0, 70, 38.0, 150, max_heart_rate=200)
        # Should produce a valid result
        assert 0 <= psi <= 10
    
    def test_invalid_core_temperature_initial(self):
        """Test that invalid initial core temperature raises ValueError."""
        with pytest.raises(ValueError):
            physiological_strain_index(34.0, 70, 38.0, 120)  # Too low
        
        with pytest.raises(ValueError):
            physiological_strain_index(41.0, 70, 38.0, 120)  # Too high
    
    def test_invalid_core_temperature_final(self):
        """Test that invalid final core temperature raises ValueError."""
        with pytest.raises(ValueError):
            physiological_strain_index(37.0, 70, 34.0, 120)  # Too low
        
        with pytest.raises(ValueError):
            physiological_strain_index(37.0, 70, 43.0, 120)  # Too high
    
    def test_invalid_heart_rate_initial(self):
        """Test that invalid initial heart rate raises ValueError."""
        with pytest.raises(ValueError):
            physiological_strain_index(37.0, 30, 38.0, 120)  # Too low
        
        with pytest.raises(ValueError):
            physiological_strain_index(37.0, 250, 38.0, 120)  # Too high
    
    def test_invalid_heart_rate_final(self):
        """Test that invalid final heart rate raises ValueError."""
        with pytest.raises(ValueError):
            physiological_strain_index(37.0, 70, 38.0, 30)  # Too low
        
        with pytest.raises(ValueError):
            physiological_strain_index(37.0, 70, 38.0, 250)  # Too high


class TestPSIInterpretation:
    """Test cases for PSI interpretation."""
    
    def test_low_strain_interpretation(self):
        """Test interpretation for low strain values."""
        interpretation = interpret_psi(1.0)
        assert "low" in interpretation.lower() or "minimal" in interpretation.lower()
    
    def test_moderate_strain_interpretation(self):
        """Test interpretation for moderate strain values."""
        interpretation = interpret_psi(4.0)
        assert "moderate" in interpretation.lower()
    
    def test_high_strain_interpretation(self):
        """Test interpretation for high strain values."""
        interpretation = interpret_psi(7.0)
        assert "high" in interpretation.lower() or "severe" in interpretation.lower()
    
    def test_extreme_strain_interpretation(self):
        """Test interpretation for extreme strain values."""
        interpretation = interpret_psi(9.0)
        assert "extreme" in interpretation.lower() or "very high" in interpretation.lower()


class TestPSIEdgeCases:
    """Test edge cases for PSI calculation."""
    
    def test_boundary_temperatures(self):
        """Test calculation at boundary temperatures."""
        # Test at minimum valid temperatures
        psi_min = physiological_strain_index(35.0, 70, 35.0, 70)
        assert 0 <= psi_min <= 10
        
        # Test at maximum valid temperatures
        psi_max = physiological_strain_index(40.0, 70, 42.0, 180)
        assert 0 <= psi_max <= 10
    
    def test_boundary_heart_rates(self):
        """Test calculation at boundary heart rates."""
        # Test at minimum valid heart rates
        psi_min = physiological_strain_index(37.0, 40, 38.0, 40)
        assert 0 <= psi_min <= 10
        
        # Test at maximum valid heart rates
        psi_max = physiological_strain_index(37.0, 200, 38.0, 220)
        assert 0 <= psi_max <= 10
    
    def test_temperature_cooling(self):
        """Test PSI when core temperature decreases."""
        psi = physiological_strain_index(38.0, 70, 37.5, 120)
        # Should handle temperature decrease gracefully
        assert 0 <= psi <= 10
    
    def test_hr_decrease(self):
        """Test PSI when heart rate decreases."""
        psi = physiological_strain_index(37.0, 120, 38.0, 80)
        # Should handle HR decrease gracefully
        assert 0 <= psi <= 10


if __name__ == "__main__":
    pytest.main([__file__]) 