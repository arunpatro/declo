class DecloList(list):
    def map(self, func):
        """Apply a function to each element in the list."""
        return DecloList(func(item) for item in self)
    
    def filter(self, predicate):
        """Filter items based on a predicate function."""
        return DecloList(item for item in self if predicate(item))
    
    def __repr__(self):
        return f"DecloList({super().__repr__()})"

def show_diff(original: str, modified: str) -> str:
    """
    Show a colored diff between original and modified code using rich for formatting.
    Red for removed lines, green for added lines.
    """
    import difflib
    from rich.console import Console
    from rich.text import Text

    console = Console(color_system="auto")
    differ = difflib.Differ()
    diff_lines = list(differ.compare(original.splitlines(True), modified.splitlines(True)))
    
    result = Text()
    prev_line = None
    for line in diff_lines:
        # Skip diff markers
        if line.startswith('?'):
            continue
        
        # If line is unchanged (starts with ' '), check if we need to show it
        if line.startswith(' '):
            # Show unchanged lines only if they're between changes
            if prev_line and prev_line.startswith(('-', '+')):
                result.append(line)
            elif not prev_line:  # First line
                result.append(line)
        # Show changed lines (removed or added)
        elif line.startswith(('-', '+')):
            result.append(line.strip('\n'), style="red" if line.startswith('-') else "green")
            result.append('\n')
        
        prev_line = line
    
    # Convert to string but maintain the rich formatting
    with console.capture() as capture:
        console.print(result, end="")
    return capture.get() 
