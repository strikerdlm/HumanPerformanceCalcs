#!/usr/bin/env python3
"""
FastAPI REST API for Human Performance Calculators.

Provides HTTP endpoints for aerospace medicine and human performance calculations.

DISCLAIMER: This API is for research and educational purposes only.
Not intended for clinical decision-making or medical device applications.

Author: Dr. Diego Malpica
Institution: Universidad Nacional de Colombia
"""

from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# Import calculators from the main package
from calculators import (
    standard_atmosphere,
    estimate_tuc,
    wbgt_indoor,
    wbgt_outdoor,
    utci,
    utci_category,
)

# Initialize FastAPI app
app = FastAPI(
    title="Human Performance Calculators API",
    description=(
        "REST API for aerospace medicine and human performance calculations. "
        "Research and educational use only."
    ),
    version="0.1.0",
    contact={
        "name": "Dr. Diego Malpica",
        "email": "dlmalpicah@unal.edu.co",
    },
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Request/Response Models ====================

class AtmosphereRequest(BaseModel):
    """Request model for standard atmosphere calculation."""
    altitude_m: float = Field(..., ge=0, le=30000, description="Altitude in meters (0-30000)")


class AtmosphereResponse(BaseModel):
    """Response model for standard atmosphere calculation."""
    pressure_pa: float = Field(..., description="Atmospheric pressure in Pascals")
    temperature_k: float = Field(..., description="Temperature in Kelvin")
    density_kg_m3: float = Field(..., description="Air density in kg/m³")
    speed_of_sound_m_s: float = Field(..., description="Speed of sound in m/s")


class TucRequest(BaseModel):
    """Request model for Time of Useful Consciousness calculation."""
    altitude_m: float = Field(..., ge=0, le=30000, description="Altitude in meters (0-30000)")
    
    @field_validator('altitude_m')
    @classmethod
    def validate_altitude(cls, v: float) -> float:
        if v < 0 or v > 30000:
            raise ValueError(f"Altitude must be between 0 and 30000 meters, got {v}")
        return v


class TucResponse(BaseModel):
    """Response model for Time of Useful Consciousness."""
    tuc_seconds: float = Field(..., description="Time of Useful Consciousness in seconds")
    tuc_minutes: float = Field(..., description="Time of Useful Consciousness in minutes")
    altitude_m: float = Field(..., description="Input altitude in meters")


class WbgtIndoorRequest(BaseModel):
    """Request model for indoor WBGT calculation."""
    natural_wet_bulb_c: float = Field(..., ge=-20, le=50, description="Natural wet bulb temperature (°C)")
    globe_temp_c: float = Field(..., ge=-20, le=80, description="Globe temperature (°C)")


class WbgtOutdoorRequest(BaseModel):
    """Request model for outdoor WBGT calculation."""
    natural_wet_bulb_c: float = Field(..., ge=-20, le=50, description="Natural wet bulb temperature (°C)")
    globe_temp_c: float = Field(..., ge=-20, le=80, description="Globe temperature (°C)")
    dry_bulb_c: float = Field(..., ge=-20, le=60, description="Dry bulb temperature (°C)")


class WbgtResponse(BaseModel):
    """Response model for WBGT calculation."""
    wbgt_c: float = Field(..., description="Wet Bulb Globe Temperature in °C")
    risk_category: Optional[str] = Field(None, description="Risk category interpretation")


class UtciRequest(BaseModel):
    """Request model for UTCI calculation."""
    air_temp_c: float = Field(..., ge=-50, le=50, description="Air temperature (°C)")
    mean_radiant_temp_c: float = Field(..., ge=-50, le=80, description="Mean radiant temperature (°C)")
    wind_speed_m_s: float = Field(..., ge=0, le=30, description="Wind speed (m/s)")
    relative_humidity_percent: float = Field(..., ge=0, le=100, description="Relative humidity (%)")


class UtciResponse(BaseModel):
    """Response model for UTCI calculation."""
    utci_c: float = Field(..., description="Universal Thermal Climate Index in °C")
    category: str = Field(..., description="Thermal stress category")
    description: str = Field(..., description="Interpretation of thermal stress")


# ==================== Root & Health Endpoints ====================

@app.get("/", tags=["General"])
async def root() -> dict[str, str]:
    """
    Root endpoint with API information.
    
    Returns:
        Dictionary with API name, version, and documentation link
    """
    return {
        "name": "Human Performance Calculators API",
        "version": "0.1.0",
        "docs": "/docs",
        "disclaimer": "Research and educational use only - not for clinical decisions",
    }


@app.get("/health", tags=["General"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Status indicating API health
    """
    return {"status": "healthy"}


# ==================== Atmosphere Calculators ====================

@app.post("/atmosphere/standard", response_model=AtmosphereResponse, tags=["Atmosphere"])
async def calculate_standard_atmosphere(request: AtmosphereRequest) -> AtmosphereResponse:
    """
    Calculate standard atmosphere properties at a given altitude.
    
    Based on International Standard Atmosphere (ISA) model.
    
    Args:
        request: AtmosphereRequest with altitude in meters
        
    Returns:
        AtmosphereResponse with pressure, temperature, density, and speed of sound
        
    Raises:
        HTTPException: If calculation fails or inputs are invalid
    """
    try:
        result = standard_atmosphere(request.altitude_m)
        return AtmosphereResponse(
            pressure_pa=result["pressure_pa"],
            temperature_k=result["temperature_k"],
            density_kg_m3=result["density_kg_m3"],
            speed_of_sound_m_s=result["speed_of_sound_m_s"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Atmosphere calculation failed: {str(e)}",
        )


@app.post("/atmosphere/tuc", response_model=TucResponse, tags=["Atmosphere"])
async def calculate_tuc(request: TucRequest) -> TucResponse:
    """
    Calculate Time of Useful Consciousness (TUC) at altitude.
    
    Estimates the time a person remains conscious and capable of useful action
    after sudden decompression or exposure to hypoxic conditions.
    
    Args:
        request: TucRequest with altitude in meters
        
    Returns:
        TucResponse with TUC in seconds and minutes
        
    Raises:
        HTTPException: If calculation fails or inputs are invalid
    """
    try:
        tuc_seconds = estimate_tuc(request.altitude_m)
        return TucResponse(
            tuc_seconds=tuc_seconds,
            tuc_minutes=tuc_seconds / 60.0,
            altitude_m=request.altitude_m,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"TUC calculation failed: {str(e)}",
        )


# ==================== Heat Stress Calculators ====================

@app.post("/heat-stress/wbgt-indoor", response_model=WbgtResponse, tags=["Heat Stress"])
async def calculate_wbgt_indoor(request: WbgtIndoorRequest) -> WbgtResponse:
    """
    Calculate indoor Wet Bulb Globe Temperature (WBGT).
    
    WBGT is used to assess heat stress in occupational and athletic settings.
    Indoor formula: WBGT = 0.7*NWB + 0.3*GT
    
    Args:
        request: WbgtIndoorRequest with natural wet bulb and globe temperatures
        
    Returns:
        WbgtResponse with calculated WBGT
        
    Raises:
        HTTPException: If calculation fails or inputs are invalid
    """
    try:
        wbgt = wbgt_indoor(request.natural_wet_bulb_c, request.globe_temp_c)
        return WbgtResponse(wbgt_c=wbgt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Indoor WBGT calculation failed: {str(e)}",
        )


@app.post("/heat-stress/wbgt-outdoor", response_model=WbgtResponse, tags=["Heat Stress"])
async def calculate_wbgt_outdoor(request: WbgtOutdoorRequest) -> WbgtResponse:
    """
    Calculate outdoor Wet Bulb Globe Temperature (WBGT).
    
    WBGT is used to assess heat stress in occupational and athletic settings.
    Outdoor formula: WBGT = 0.7*NWB + 0.2*GT + 0.1*DB
    
    Args:
        request: WbgtOutdoorRequest with natural wet bulb, globe, and dry bulb temperatures
        
    Returns:
        WbgtResponse with calculated WBGT
        
    Raises:
        HTTPException: If calculation fails or inputs are invalid
    """
    try:
        wbgt = wbgt_outdoor(
            request.natural_wet_bulb_c,
            request.globe_temp_c,
            request.dry_bulb_c,
        )
        return WbgtResponse(wbgt_c=wbgt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Outdoor WBGT calculation failed: {str(e)}",
        )


# ==================== Thermal Comfort Calculators ====================

@app.post("/thermal/utci", response_model=UtciResponse, tags=["Thermal Comfort"])
async def calculate_utci(request: UtciRequest) -> UtciResponse:
    """
    Calculate Universal Thermal Climate Index (UTCI).
    
    UTCI assesses thermal stress in outdoor environments, accounting for
    air temperature, radiant temperature, wind speed, and humidity.
    
    Reference:
    - Błażejczyk et al. (2012). An introduction to the Universal Thermal Climate Index (UTCI).
      Geographia Polonica, 85(1), 5-10.
    
    Args:
        request: UtciRequest with meteorological parameters
        
    Returns:
        UtciResponse with UTCI value, category, and interpretation
        
    Raises:
        HTTPException: If calculation fails or inputs are invalid
    """
    try:
        utci_value = utci(
            request.air_temp_c,
            request.mean_radiant_temp_c,
            request.wind_speed_m_s,
            request.relative_humidity_percent,
        )
        category = utci_category(utci_value)
        
        # Interpretation mapping
        category_descriptions = {
            "extreme_cold_stress": "Extreme cold stress - dangerous conditions",
            "very_strong_cold_stress": "Very strong cold stress - high risk",
            "strong_cold_stress": "Strong cold stress - caution advised",
            "moderate_cold_stress": "Moderate cold stress",
            "slight_cold_stress": "Slight cold stress",
            "no_thermal_stress": "No thermal stress - comfortable",
            "moderate_heat_stress": "Moderate heat stress",
            "strong_heat_stress": "Strong heat stress - caution advised",
            "very_strong_heat_stress": "Very strong heat stress - high risk",
            "extreme_heat_stress": "Extreme heat stress - dangerous conditions",
        }
        
        return UtciResponse(
            utci_c=utci_value,
            category=category,
            description=category_descriptions.get(category, "Unknown category"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"UTCI calculation failed: {str(e)}",
        )


# ==================== Error Handlers ====================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Invalid input: {str(exc)}"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"},
    )
