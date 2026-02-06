import pytest
import swisseph as swe
from dataclasses import FrozenInstanceError # For strict immutability check

from kerykeion.vedic.registry import (
    resolve_ayanamsa,
    resolve_house_system,
    HouseFetchPlan,
    VedicRegistryError,
)

def test_registry_ayanamsa_resolution():
    """Verify correct resolution and mapping of Ayanamsa modes."""
    # Test case-insensitive
    spec = resolve_ayanamsa("Lahiri")
    assert spec.id == "lahiri"
    assert spec.swe_mode == swe.SIDM_LAHIRI

    # Test invalid input
    with pytest.raises(VedicRegistryError) as excinfo:
        resolve_ayanamsa("invalid_mode")
    assert "Available:" in str(excinfo.value)

    # Test None/Empty input (New Guard)
    with pytest.raises(VedicRegistryError):
        resolve_ayanamsa(None)
    with pytest.raises(VedicRegistryError):
        resolve_ayanamsa("   ")

def test_registry_house_system_resolution():
    """Verify House System strategies (Fetch Plans)."""
    ws_spec = resolve_house_system("Whole_Sign") # Mixed case test

    assert ws_spec.fetch_plan == HouseFetchPlan.ASC_ONLY
    assert ws_spec.swe_hsys_code is None

    # Test invalid system
    with pytest.raises(VedicRegistryError):
        resolve_house_system("invalid_system")

    # Test None/Empty input
    with pytest.raises(VedicRegistryError):
        resolve_house_system("")
    with pytest.raises(VedicRegistryError):
        resolve_house_system(None)
    with pytest.raises(VedicRegistryError):
        resolve_house_system("   ")

def test_registry_immutability():
    """Ensure Specs are frozen dataclasses using the specific error type."""
    spec = resolve_ayanamsa("lahiri")

    # Using FrozenInstanceError is more precise than generic AttributeError
    with pytest.raises(FrozenInstanceError):
        spec.swe_mode = 123