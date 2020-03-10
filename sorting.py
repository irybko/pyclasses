# -*- utf-8 -*-
###########################################
# PSF license aggrement for algorithms.py
# Developed by Ivan Rybko
# Searching Sorting
###########################################

class Sorting:
    def __init__(self, method):
        self.method = method

    def cycleSort(self, array):
        writes = 0

        # Loop through the array to find cycles to rotate. 
        for cycleStart in range(0, len(array) - 1): 
            item = array[cycleStart] 
        
            # Find where to put the item. 
            pos = cycleStart
            for i in range(cycleStart + 1, len(array)):
                if array[i] < item:
                    pos += 1
        
            # If the item is already there, this is not a cycle.
            if pos == cycleStart:
                continue
            # Otherwise, put the item there or right after any duplicates. 
            while(item == array[pos]):
                pos += 1
            array[pos], item = item, array[pos] 
            writes += 1
      
            # Rotate the rest of the cycle. 
            while(pos != cycleStart):
                # Find where to put the item. 
                pos = cycleStart 
                for i in range(cycleStart + 1, len(array)): 
                    if array[i] < item:
                        pos += 1
        
            # Put the item there or right after any duplicates. 
            while(item == array[pos]):
                pos += 1
            array[pos], item = item, array[pos] 
            writes += 1
        return writes 
    
    def bubbleSort(self, arr):
        n = len(arr) 
        # Traverse through all array elements 
        for i in range(n):
            # Last i elements are already in place 
            for j in range(0, n-i-1):
                # traverse the array from 0 to n-i-1 
                # Swap if the element found is greater 
                # than the next element 
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]

    def partition(self, arr,low,high):
        # This function takes last element as pivot, places 
        # the pivot element at its correct position in sorted 
        # array, and places all smaller (smaller than pivot) 
        # to left of pivot and all greater elements to right 
        # of pivot
        i = ( low-1 )         # index of smaller element 
        pivot = arr[high]     # pivot 
        
        for j in range(low , high):
            # If current element is smaller than or 
            # equal to pivot 
            if arr[j] <= pivot:
                
                # increment index of smaller element 
                i = i+1 
                arr[i],arr[j] = arr[j],arr[i] 
  
                arr[i+1],arr[high] = arr[high],arr[i+1] 
        return ( i+1 ) 
  
        # The main function that implements QuickSort 
        # arr[] --> Array to be sorted, 
        # low  --> Starting index, 
        # high  --> Ending index 
        # Function to do Quick sort 
    def quickSort(self, arr,low,high): 
        if low < high:
            # pi is partitioning index, arr[p] is now 
            # at right place 
            pi = partition(arr,low,high) 
  
            # Separately sort elements before 
            # partition and after partition 
            quickSort(arr, low, pi-1) 
            quickSort(arr, pi+1, high) 

    def shellSort(self, arr):
        # Start with a big gap, then reduce the gap 
        n = len(arr) 
        gap = n//2
  
        # Do a gapped insertion sort for this gap size. 
        # The first gap elements a[0..gap-1] are already in gapped  
        # order keep adding one more element until the entire array 
        # is gap sorted 
        while(gap > 0):
            for i in range(gap,n):
                
                # add a[i] to the elements that have been gap sorted 
                # save a[i] in temp and make a hole at position i 
                temp = arr[i] 
  
                # shift earlier gap-sorted elements up until the correct 
                # location for a[i] is found 
                j = i 
                while  j >= gap and arr[j-gap] >temp: 
                    arr[j] = arr[j-gap] 
                    j -= gap 
  
                # put temp (the original a[i]) in its correct location 
                arr[j] = temp 
        gap //= 2
  
    # Function to do insertion sort 
    def insertionSort(self, arr):
        # Traverse through 1 to len(arr) 
        for i in range(1, len(arr)):

            key = arr[i]

            # Move elements of arr[0..i-1], that are 
            # greater than key, to one position ahead 
            # of their current position 
            j = i-1
            while j >= 0 and key < arr[j]:
                arr[j + 1] = arr[j] 
                j -= 1
                arr[j + 1] = key 

        # Traverse through all array elements 
        for i in range(len(A)): 
      
            # Find the minimum element in remaining  
            # unsorted array 
            min_idx = i 
       
            for j in range(i+1, len(A)):
                if A[min_idx] > A[j]:
                    min_idx = j 
              
            # Swap the found minimum element with  
            # the first element         
            A[i], A[min_idx] = A[min_idx], A[i] 
