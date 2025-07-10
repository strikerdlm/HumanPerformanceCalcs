"""
Unit tests for WCT.py (Wind Chill Temperature Calculator)
"""
import pytest
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WCT import wind_chill_temperature, interpret_wind_chill


class TestWindChillCalculation:
    """Test cases for wind chill temperature calculation."""
    
    def test_basic_calculation_celsius(self):
        """Test basic wind chill calculation in Celsius."""
        # Test case: 0°C, 10 m/s wind
        wind_chill = wind_chill_temperature(0.0, 10.0, 'celsius')
        # Expected: approximately -10.5°C based on NOAA formula
        assert -12.0 < wind_chill < -9.0
    
    def test_basic_calculation_fahrenheit(self):
        """Test basic wind chill calculation in Fahrenheit."""
        # Test case: 32°F (0°C), 22.37 mph (10 m/s) wind
        wind_chill = wind_chill_temperature(0.0, 10.0, 'fahrenheit')
        # Expected: approximately 13°F based on NOAA formula
        assert 10.0 < wind_chill < 16.0
    
    def test_minimal_wind(self):
        """Test calculation with minimal wind speed."""
        wind_chill = wind_chill_temperature(-5.0, 1.34, 'celsius')
        # Should be colder than air temperature
        assert wind_chill < -5.0
    
    def test_high_wind(self):
        """Test calculation with high wind speed."""
        wind_chill = wind_chill_temperature(-10.0, 20.0, 'celsius')
        # Should be significantly colder than air temperature
        assert wind_chill < -15.0
    
    def test_invalid_temperature(self):
        """Test that temperatures above 10°C raise ValueError."""
        with pytest.raises(ValueError):
            wind_chill_temperature(15.0, 5.0, 'celsius')
    
    def test_invalid_wind_speed(self):
        """Test that wind speeds below 1.34 m/s raise ValueError."""
        with pytest.raises(ValueError):
            wind_chill_temperature(0.0, 1.0, 'celsius')
    
    def test_invalid_output_unit(self):
        """Test that invalid output units raise ValueError."""
        with pytest.raises(ValueError):
            wind_chill_temperature(0.0, 5.0, 'kelvin')


class TestWindChillInterpretation:
    """Test cases for wind chill interpretation."""
    
    def test_safe_conditions(self):
        """Test interpretation for safe conditions."""
        interpretation = interpret_wind_chill(-5.0)
        assert "Low risk" in interpretation or "safe" in interpretation.lower()
    
    def test_moderate_risk(self):
        """Test interpretation for moderate risk conditions."""
        interpretation = interpret_wind_chill(-15.0)
        assert "Moderate" in interpretation or "caution" in interpretation.lower()
    
    def test_high_risk(self):
        """Test interpretation for high risk conditions."""
        interpretation = interpret_wind_chill(-25.0)
        assert "High" in interpretation or "danger" in interpretation.lower()
    
    def test_extreme_risk(self):
        """Test interpretation for extreme risk conditions."""
        interpretation = interpret_wind_chill(-40.0)
        assert "Extreme" in interpretation or "frostbite" in interpretation.lower()


class TestWindChillEdgeCases:
    """Test edge cases for wind chill calculation."""
    
    def test_boundary_temperature(self):
        """Test calculation at boundary temperature (10°C)."""
        wind_chill = wind_chill_temperature(10.0, 5.0, 'celsius')
        # Wind chill should be less than air temperature
        assert wind_chill < 10.0
    
    def test_boundary_wind_speed(self):
        """Test calculation at boundary wind speed (1.34 m/s)."""
        wind_chill = wind_chill_temperature(0.0, 1.34, 'celsius')
        # Should produce a valid result
        assert wind_chill < 0.0
    
    def test_very_cold_temperature(self):
        """Test calculation with very cold temperature."""
        wind_chill = wind_chill_temperature(-30.0, 10.0, 'celsius')
        # Should be significantly colder
        assert wind_chill < -35.0


if __name__ == "__main__":
    pytest.main([__file__]) 