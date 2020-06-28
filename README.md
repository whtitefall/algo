# Algorithm-Template

Aiming to find generic algorithm solution 

***
### Two pointer (equi directional )


[209. Minimum Size Subarray Sum](https://leetcode.com/problems/minimum-size-subarray-sum/)

[930. Binary Subarrays With Sum](https://leetcode.com/problems/binary-subarrays-with-sum/)  
More like an equi three pointer, because its binary limitation and countting requirements
[209. Minimum Size Subarray Sum](https://leetcode.com/problems/minimum-size-subarray-sum/)  
Similar to dynamic sliding window.

***

### Two pointer (opposite directional)  Needs sort



[881. Boats to Save People](https://leetcode.com/problems/boats-to-save-people/)  
Move and compare

***

### Sliding window (similar to equi directional two pointer)

[713. Subarray Product Less Than K](https://leetcode.com/problems/subarray-product-less-than-k/)  
Dynamic sliding window, similarr to two pointer equi directional. 

[3. Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/)  
Dynamic sliding window

[567. Permutation in String](https://leetcode.com/problems/permutation-in-string/)  
Fixed sliding window, differnt from 713


[978. Longest Turbulent Subarray](https://leetcode.com/problems/longest-turbulent-subarray/)

Dynamic sliding window

[424. Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/)  
Dynamic sliding window 

***
### Floyd's cycle (equi two pointer similar)

[287. Find the Duplicate Number](https://leetcode.com/problems/find-the-duplicate-number/)  
Two phase cycle, 1st phase intersection, 2nd phase meet at entrance of cycle


***

### Binary Search

[33. Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/)  
Modified binary search, find pivot first

[658. Find K Closest Elements](https://leetcode.com/problems/find-k-closest-elements/)  
1.binary search 2.expand around target value


***

### Dynamic programming 

[300. Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/)  
remmber longgest sequence length at each step. n^2  
can be improved using binary search, searching desired numbers and insert into current dp sequence.