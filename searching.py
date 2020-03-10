# -*- utf-8 -*-
###########################################
# PSF license aggrement for algorithms.py
# Developed by Ivan Rybko
# Searching Sorting
###########################################

class Searching:
    def __init__(self, arr, method):
        self.data = arr
        self.alg  = method

    def linearsearch(self, arr, n, x):
        for i in range (0, n):
            if arr[i] == x:
                return i
            else:
                return -1

    def binarySearch(self, l, r, x):
        # Check base case 
        if r >= l:
            mid = l + (r - l)/2
            # If element is present at the middle itself 
            if arr[mid] == x: 
                return mid 
        # If element is smaller than mid, then it  
        # can only be present in left subarray 
            elif arr[mid] > x:
                 return self.binarySearch(arr, l, mid-1, x) 
  
            # Else the element can only be present  
            # in right subarray 
            else: 
                return self.binarySearch(arr, mid + 1, r, x) 
        # Element is not present in the array 
        else:
            return -1
   
    def ternarySearch(self, arr=[], l=int, r=int, x=int):
        if r >= l:
            mid1 = l + (r - l)/3 
            mid2 = mid1 + (r - l)/3
  
            # If x is present at the mid1 
            if arr[mid1] == x:  return mid1
  
            # If x is present at the mid2 
            if arr[mid2] == x:  return mid2

            # If x is present in left one-third
            if arr[mid1] > x: return self.ternarySearch(arr, l, mid1-1, x)
            
            # If x is present in right one-third
            if arr[mid2] < x: return self.ternarySearch(arr, mid2+1, r, x)

            # If x is present in middle one-third
            return self.ternarySearch(arr, mid1+1, mid2-1, x)
        # We reach here when element is not present in array 
        return -1
    
    def jumpSearch(self, arr , x , n ):
        # Finding block size to be jumped 
        step = math.sqrt(n) 
      
        # Finding the block where element is 
        # present (if it is present) 
        prev = 0
        while(arr[int(min(step, n)-1)] < x):
            prev = step
            step += math.sqrt(n)

            if prev >= n:
                return -1
      
        # Doing a linear search for x in  
        # block beginning with prev.
        while(arr[int(prev)] < x):
            prev += 1
          
        # If we reached next block or end  
        # of array, element is not present. 
        if prev == min(step, n): 
            return -1
      
        # If element is found 
        if arr[int(prev)] == x:
            return prev
        else:
            return -1

    def interpolationSearch(self, arr, n, x):
        # Find indexs of two corners 
        lo = 0
        hi = (n - 1) 
   
        # Since array is sorted, an element present 
        # in array must be in range defined by corner 
        while(lo <= hi and x >= arr[lo] and x <= arr[hi]):
            if lo == hi:
                if arr[lo] == x:
                    return lo
                else:
                    return -1; 
          
        # Probing the position with keeping 
        # uniform distribution in mind. 
        pos  = lo + int(((float(hi - lo) / ( arr[hi] - arr[lo])) * ( x - arr[lo]))) 
  
        # Condition of target found 
        if arr[pos] == x: 
            return pos 
   
        # If x is larger, x is in upper part 
        if arr[pos] < x: 
            lo = pos + 1;
        # If x is smaller, x is in lower part 
        else:
            hi = pos - 1
            return -1

    def exponentialSearch(arr, n, x): 
        # Returns the position of first 
        # occurence of x in array 
        # IF x is present at first  
        # location itself
        if arr[0] == x:
            return 0
    
        # Find range for binary search  
        # j by repeated doubling 
        i = 1
        while(i < n and arr[i] <= x):
            i = i * 2
      
        # Call binary search for the found range 
        return self.binarySearch( arr, i / 2, min(i, n), x)

