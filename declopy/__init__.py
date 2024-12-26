from .enhanced_list import EnhancedList
from .compiler import transform_file

__version__ = "0.1.0"
__all__ = ["EnhancedList", "transform_file"]

# declo/enhanced_list.py
class EnhancedList(list):
    def map(self, func):
        """Apply a function to each element in the list."""
        return EnhancedList(func(item) for item in self)
    
    def filter(self, predicate):
        """Filter items based on a predicate function."""
        return EnhancedList(item for item in self if predicate(item))
    
    def __repr__(self):
        return f"EnhancedList({super().__repr__()})"
