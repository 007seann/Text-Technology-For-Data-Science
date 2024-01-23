class PostingNode:
    """
    Represents posting node.
    
    params:
        value: value/index represented by posting node.
    """
    def __init__(self, value):
        self.value = value
        self.next = None
        self.skip = None # pointer to next skip.