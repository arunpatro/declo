class DecloList(list):
    def map(self, func):
        """Apply a function to each element in the list."""
        return DecloList(func(item) for item in self)
    
    def filter(self, predicate):
        """Filter items based on a predicate function."""
        return DecloList(item for item in self if predicate(item))
    
    def __repr__(self):
        return f"DecloList({super().__repr__()})" 
