import swisseph as swe
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from types import MappingProxyType

class HouseFetchPlan(str, Enum):
    """
    Strategy for fetching house data from SwissEph.
    Determines if we need full house cusp calculation or just the Ascendant.
    """
    ASC_ONLY = "asc_only"
    HOUSES_EX = "houses_ex"

@dataclass(frozen=True)
class AyanamsaSpec:
    id: str
    swe_mode: int
    t0: Optional[float] = None  # Future-proofing (e.g. for SIDM_USER scenarios)

@dataclass(frozen=True)
class HouseSystemSpec:
    id: str
    fetch_plan: HouseFetchPlan
    swe_hsys_code: Optional[str] = None  # Required iff fetch_plan == HOUSES_EX

class VedicRegistryError(ValueError):
    """Invalid registry configuration or unsupported user setting."""
    pass

# --- Internal Data ---

_AYANAMSA_DATA = {
    "lahiri": AyanamsaSpec("lahiri", swe.SIDM_LAHIRI),
    # Future expansions go here
}

_HOUSE_SYSTEM_DATA = {
    "whole_sign": HouseSystemSpec("whole_sign", fetch_plan=HouseFetchPlan.ASC_ONLY),
    # "sripati": HouseSystemSpec("sripati", fetch_plan=HouseFetchPlan.HOUSES_EX, swe_hsys_code="P"),
}

# --- Internal Validation Logic ---

def _validate_house_spec(spec: HouseSystemSpec) -> None:
    """Ensures logic consistency for house systems before returning spec."""
    if spec.fetch_plan == HouseFetchPlan.HOUSES_EX:
        if not spec.swe_hsys_code or len(spec.swe_hsys_code) != 1:
            raise VedicRegistryError(
                f"HouseSystemSpec '{spec.id}' requires a single-character swe_hsys_code when fetch_plan=HOUSES_EX."
            )

# --- Fail-Fast: Validate Registry on Import ---
# This prevents silent bugs by crashing immediately if a developer adds an invalid spec.
for _spec in _HOUSE_SYSTEM_DATA.values():
    _validate_house_spec(_spec)

# --- Public Read-Only Registry Views ---
AYANAMSA_REGISTRY = MappingProxyType(_AYANAMSA_DATA)
HOUSE_SYSTEM_REGISTRY = MappingProxyType(_HOUSE_SYSTEM_DATA)

# --- Public Resolvers ---

def resolve_ayanamsa(mode: str) -> AyanamsaSpec:
    """Resolves string input to AyanamsaSpec. Case-insensitive."""
    if mode is None or not str(mode).strip():
        raise VedicRegistryError("Ayanamsa mode must be a non-empty string")

    key = str(mode).strip().casefold() # Robust unicode handling
    spec = AYANAMSA_REGISTRY.get(key)

    if spec is None:
        raise VedicRegistryError(
            f"Invalid Ayanamsa mode: '{mode}'. Available: {sorted(AYANAMSA_REGISTRY.keys())}"
        )
    return spec

def resolve_house_system(sys_id: str) -> HouseSystemSpec:
    """Resolves string input to HouseSystemSpec. Case-insensitive."""
    if sys_id is None or not str(sys_id).strip():
        raise VedicRegistryError("House system must be a non-empty string")

    key = str(sys_id).strip().casefold()
    spec = HOUSE_SYSTEM_REGISTRY.get(key)

    if spec is None:
        raise VedicRegistryError(
            f"Invalid House System: '{sys_id}'. Available: {sorted(HOUSE_SYSTEM_REGISTRY.keys())}"
        )
    # Double-check (though we validated on import, strictness helps)
    _validate_house_spec(spec)
    return spec