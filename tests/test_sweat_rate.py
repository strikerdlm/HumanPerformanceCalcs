"""
Unit tests for SimpleSweatRate.py
"""
import pytest
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SimpleSweatRate import calculate_sweat_rate, get_dehydration_percentage, interpret_sweat_rate, interpret_dehydration


class TestSweatRateCalculation:
    """Test cases for sweat rate calculation function."""
    
    def test_basic_calculation(self):
        """Test basic sweat rate calculation."""
        # Test case: 2kg weight loss, 1L fluid intake, 0.5L urine, 2 hours
        sweat_rate = calculate_sweat_rate(70.0, 68.0, 1.0, 0.5, 2.0)
        expected = (2.0 + 1.0 - 0.5) / 2.0  # 1.25 L/h
        assert abs(sweat_rate - expected) < 0.001
    
    def test_no_weight_loss(self):
        """Test calculation with no weight loss."""
        sweat_rate = calculate_sweat_rate(70.0, 70.0, 1.0, 0.5, 2.0)
        expected = (0.0 + 1.0 - 0.5) / 2.0  # 0.25 L/h
        assert abs(sweat_rate - expected) < 0.001
    
    def test_negative_weight_change(self):
        """Test calculation with weight gain (negative weight loss)."""
        sweat_rate = calculate_sweat_rate(70.0, 71.0, 1.0, 0.5, 2.0)
        expected = (-1.0 + 1.0 - 0.5) / 2.0  # -0.25 L/h
        assert abs(sweat_rate - expected) < 0.001
    
    def test_invalid_inputs(self):
        """Test that invalid inputs raise ValueError."""
        with pytest.raises(ValueError):
            calculate_sweat_rate(0.0, 70.0, 1.0, 0.5, 2.0)  # Zero weight
        
        with pytest.raises(ValueError):
            calculate_sweat_rate(70.0, 68.0, -1.0, 0.5, 2.0)  # Negative fluid intake
        
        with pytest.raises(ValueError):
            calculate_sweat_rate(70.0, 68.0, 1.0, 0.5, 0.0)  # Zero duration
        
        with pytest.raises(ValueError):
            calculate_sweat_rate(70.0, 65.0, 1.0, 0.5, 2.0)  # Unrealistic weight loss


class TestDehydrationPercentage:
    """Test cases for dehydration percentage calculation."""
    
    def test_basic_dehydration(self):
        """Test basic dehydration percentage calculation."""
        dehydration = get_dehydration_percentage(70.0, 68.0)
        expected = (2.0 / 70.0) * 100  # 2.86%
        assert abs(dehydration - expected) < 0.01
    
    def test_no_dehydration(self):
        """Test with no weight loss."""
        dehydration = get_dehydration_percentage(70.0, 70.0)
        assert dehydration == 0.0
    
    def test_weight_gain(self):
        """Test with weight gain (negative dehydration)."""
        dehydration = get_dehydration_percentage(70.0, 71.0)
        expected = (-1.0 / 70.0) * 100  # -1.43%
        assert abs(dehydration - expected) < 0.01


class TestInterpretations:
    """Test cases for interpretation functions."""
    
    def test_sweat_rate_interpretations(self):
        """Test sweat rate interpretation categories."""
        assert "Low" in interpret_sweat_rate(0.5)
        assert "Moderate" in interpret_sweat_rate(1.0)
        assert "High" in interpret_sweat_rate(2.0)
        assert "Very high" in interpret_sweat_rate(3.0)
    
    def test_dehydration_interpretations(self):
        """Test dehydration interpretation categories."""
        assert "Minimal" in interpret_dehydration(0.5)
        assert "Mild" in interpret_dehydration(1.5)
        assert "Moderate" in interpret_dehydration(2.5)
        assert "Severe" in interpret_dehydration(4.0)


if __name__ == "__main__":
    pytest.main([__file__]) 