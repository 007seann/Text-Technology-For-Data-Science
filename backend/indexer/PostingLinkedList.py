import math
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
class PostingLinkedList:
    """
    LinkedList representing posting nodes. 
    params:         
        initial_values: list of values to initialise the list with.
    
    """
    def __init__(self, initial_values = []):
        self.head, self.tail = None, None  # Maintain tail pointer for faster sorted insertions. Reduce O(sqrt(insertion time))
        self.length = 0 # used to maintain skip pointer gaps. 
        self.skip_size = 0 # gaps between skip pointers.
        self.min_skip_size = 3 # only insert skip pointers if skip size greater than min_skip_size
        
        #Initialise Postings List if initialised with a list. 
        if initial_values:
            for value in initial_values:
                self.insert(value)
    
    #Object functions used for print operations      
    def __str__(self) -> str:
        return " --> ".join(map(str, self.toList()))
    
    def __repr__(self) -> str:
        return "[" + ", ".join(map(str, self.toList())) + "]"
    
    def __len__(self):
        return self.length

    # Serialisation support
    def __getstate__(self):
        return {'initial_values': self.toList()}
    
    def __setstate__(self, state):
        self.__init__(state['initial_values'])
    
    # Used during intersection operation for phrase and proximity search
    def decrement_postings(self, amount):
        current = self.head
        decremented_list = PostingLinkedList([current.value - amount])
        while current.next:
            current = current.next
            decremented_list.insert(current.value - amount)
        return decremented_list
    
    def insert(self, value):
        new_node = PostingNode(value)
        if not self.head or value < self.head.value:
            new_node.next = self.head
            self.head = new_node
            if not self.tail:
                self.tail = self.head  # Set tail if list was empty
        else:
            prev, curr = self.head, self.head.next
            while curr and curr.value < value:
                prev, curr = curr, curr.next
            if curr and curr.value == value:
                return  # Value already exists
            new_node.next = curr
            prev.next = new_node
            if not curr:  # Update tail if new_node is now the last node
                self.tail = new_node
        
        self.length += 1
        self._adjust_skip_pointers_if_needed()


    def _adjust_skip_pointers_if_needed(self):
        new_skip_size = int(math.sqrt(self.length))
        if new_skip_size != self.skip_size and new_skip_size > self.min_skip_size:
            self.skip_size = new_skip_size
            self._adjust_skip_pointers()

    def _adjust_skip_pointers(self):
        current = previous = self.head
        skip_counter = self.skip_size

        while current and current.next:
            current = current.next
            current.skip = None  # Reset any old references
            skip_counter -= 1

            if skip_counter == 0:
                previous.skip = current
                previous = current
                skip_counter = self.skip_size

        if previous != current:  # Ensure the last skip pointer is set correctly
            previous.skip = current
        
    def intersect(self, posting_list):
        p1, p2 = self.head, posting_list.head
        result = PostingLinkedList()
        
        while (p1 and p2):
            if p1.value == p2.value:
                result.insert(p1.value)
                p1, p2 = p1.next, p2.next
            elif p1.value < p2.value:
                p1 = p1.next
            else:
                p2 = p2.next
        return result
    
    def union(self, posting_list):
        p1, p2 = self.head, posting_list.head
        result_posting = PostingLinkedList()
        
        while p1 and p2:
            if p1.value < p2.value:
                result_posting.insert(p1.value)
                p1 = p1.next
            elif p2.value < p1.value:
                result_posting.insert(p2.value)
                p2 = p2.next
            else:
                result_posting.insert(p1.value)
                p1, p2 = p1.next, p2.next
            # Append remaining values from non-empty list
        while p1:
            result_posting.insert(p1.value)
            p1 = p1.next
        while p2:
            result_posting.insert(p2.value)
            p2 = p2.next
        return result_posting
    
    # Convert postings list to regular list. 
    def toList(self):
        list_cache = []
        current = self.head
        while current:
            list_cache.append(current.value)
            current = current.next
        return list_cache
