from __future__ import annotations

import math
import types
import warnings
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseUnit
    from .compat import ContextDict, NumericLike

from ..exceptions import DimensionMismatchError
from .compat import HAS_RAPIDFUZZ

# =========================================================================
# 1. ONTOLOGY & DISCRETE CONCEPTS (Categorical Semantic Mapping)
# =========================================================================

class Concept:
    """
    Represents a discrete semantic entity within an Ontology.
    """
    def __init__(self, aliases: list[str] | types.EllipsisType | None = ...) -> None:
        """
        Represents a discrete semantic entity within an Ontology.

        Args:
            aliases: A list of dirty strings/aliases that should automatically map to this concept.
                     Defaults to `...` (Ellipsis), which tells the engine to auto-generate 
                     aliases based on the assigned variable name.
        """
        self.aliases: list[str] = [] if isinstance(aliases, types.EllipsisType) else (aliases or [])
        self.name: str = ""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"

class _OntologyMeta(type):
    """Metaclass that registers and manages Concepts within an Ontology."""
    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> _OntologyMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        concepts: dict[str, Concept] = {}
        for key, val in namespace.items():
            if isinstance(val, Concept):
                val.name = key
                if not val.aliases:
                    val.aliases = [key.replace('_', ' ').lower(), key] 
                concepts[key] = val
        cls.__phaethon_concepts__ = concepts
        return cls

class Ontology(metaclass=_OntologyMeta):
    """
    Base class for defining categorical business domains and taxonomies.
    """
    __phaethon_concepts__: dict[str, Concept]

    @classmethod
    def match(cls, raw_str: str | Any, fuzzy_match: bool = False, confidence: float = 0.85) -> str | None:
        """
        Matches a raw string against the ontology's canonical concepts and aliases.

        Args:
            raw_str: The raw, dirty input string to be classified.
            fuzzy_match: If True, uses string metrics to find the closest 
                         matching alias if an exact match fails.
            confidence: The minimum similarity score (0.0 to 1.0) required to accept 
                        a fuzzy match. Defaults to 0.85 (85%).

        Returns:
            The official string name of the matched Concept, or None if no match is found.
        """
        if not isinstance(raw_str, str) or not raw_str.strip():
            return None
            
        raw_lower = raw_str.strip().lower()
        
        # 1. EXACT MATCHING
        for name, concept in cls.__phaethon_concepts__.items():
            if raw_lower == name.lower():
                return name
            if any(raw_lower == alias.lower() for alias in concept.aliases):
                return name
                
        # 2. FUZZY MATCHING
        if fuzzy_match:
            if not HAS_RAPIDFUZZ:
                warnings.warn(
                    "\033[33m[Phaethon Degradation]\033[0m 'fuzzy_match=True' requested in Ontology.match(), "
                    "but 'rapidfuzz' is not installed. Falling back to exact string match. ",
                    UserWarning
                )
            else:
                from rapidfuzz import process, fuzz
                
                # Flatten the ontology dictionary for the fuzzy search space
                search_dict: dict[str, str] = {}
                for name, concept in cls.__phaethon_concepts__.items():
                    search_dict[name.lower()] = name
                    for alias in concept.aliases:
                        search_dict[alias.lower()] = name
                        
                # Extract the best match
                match = process.extractOne(
                    raw_lower, 
                    search_dict.keys(), 
                    scorer=fuzz.ratio
                )
                
                if match:
                    best_str, score, _ = match
                    if score >= (confidence * 100.0):
                        return search_dict[best_str]
                    
        return None
    
    @classmethod
    def options(cls) -> dict[str, list[str]]:
        """
        Returns the canonical concepts and their valid aliases.
        Highly useful for exporting Data Governance dictionaries or UI dropdown options.
        """
        return {name: concept.aliases for name, concept in cls.__phaethon_concepts__.items()}

# =========================================================================
# 2. SEMANTIC STATES & CONDITIONS (Physics-to-Category Translation)
# =========================================================================

class Condition:
    """
    Defines the physical boundaries required to trigger a specific SemanticState.
    """
    def __init__(
        self, 
        target_unit: type[BaseUnit], 
        min: NumericLike | None = None, 
        max: NumericLike | None = None
    ) -> None:
        """
        Defines the physical boundaries required to trigger a specific SemanticState.

        Args:
            target_unit: The strict physical unit class to which the raw data must be 
                         converted before evaluation (e.g., u.Celsius).
            min: The absolute minimum numeric boundary for this condition to trigger.
            max: The absolute maximum numeric boundary for this condition to trigger.
        """
        self.target_unit = target_unit
        self.min = min
        self.max = max
        self.name: str = ""

class _SemanticStateMeta(type):
    """
    Metaclass that orchestrates the evaluation of multiple Conditions to 
    classify continuous physical vectors into discrete string categories.
    """
    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> _SemanticStateMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        conditions: dict[str, Condition] = {}
        for key, val in namespace.items():
            if isinstance(val, Condition):
                val.name = key
                conditions[key] = val
        cls.__phaethon_conditions__ = conditions
        return cls

class SemanticState(metaclass=_SemanticStateMeta):
    """
    Base class for classifying continuous physical values into semantic logic.
    """
    __phaethon_conditions__: dict[str, Condition]

    @classmethod
    def classify(
        cls, 
        raw_mag: NumericLike, 
        raw_unit_cls: type[BaseUnit] | None, 
        active_context: ContextDict | None = None
    ) -> str | None:
        """
        Evaluates a raw physical magnitude and its unit against all defined Conditions.

        This method automatically standardizes the unit dimensional matching before
        checking the `min` and `max` boundaries of each condition.

        Args:
            raw_mag: The raw numeric value of the physical property.
            raw_unit_cls: The original unit class of the raw magnitude (e.g., u.Fahrenheit).
            active_context: Optional dictionary of environmental variables (e.g., exchange rates) 
                            to inject dynamically during the evaluation.

        Returns:
            The official string name of the satisfied SemanticState, or None if it 
            falls out of bounds or if a dimension mismatch occurs.
        """
        try:
            if raw_unit_cls is None or math.isnan(float(raw_mag)): # type: ignore
                return None
        except (TypeError, ValueError):
            return None
            
        ctx = active_context or {}
            
        for name, condition in cls.__phaethon_conditions__.items():
            try:
                raw_instance = raw_unit_cls(raw_mag, context=ctx)
                
                target_instance = raw_instance.to(condition.target_unit)
                val = float(target_instance.mag)
                
                if condition.min is not None and val < float(condition.min):
                    continue
                if condition.max is not None and val > float(condition.max):
                    continue
                    
                return name
                
            except DimensionMismatchError:
                continue
            except Exception:
                continue
                
        return None