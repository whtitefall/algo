# Google 题目统计与分类

> 整理日期：2026-09-25。hack2hire.com 与 leetcode.com 在整理环境中无法直连，数据来自下面列出的公开镜像，请以原站为准。

## 数据来源

| 来源 | 实际使用的数据 | 快照时间 | 题数 |
| --- | --- | --- | --- |
| [hack2hire · Google coding questions](https://www.hack2hire.com/question-bank/companies/google/coding-questions) | 官方仓库 [hack2hire-com/SDE-interview-question](https://github.com/hack2hire-com/SDE-interview-question) README 的 Google 部分 | 2025-06-19 | 高频 LC 27 道（原表 29 行，806 / 1825 重复）+ 非 LC 原创题 10 道 |
| [LeetCode · Google · 30 天](https://leetcode.com/company/google/?favoriteSlug=google-thirty-days) | 镜像 [liquidslr/leetcode-company-wise-problems](https://github.com/liquidslr/leetcode-company-wise-problems) `Google/1. Thirty Days.csv` | 2026-08-16 | 183 |

搜索引擎摘要显示 hack2hire 的 Google 题库在不同时间有 46+ / 69 / 81 道，公开仓库只放出了其中的 Top 10 非 LC 题，所以第一部分只是样本，不是全集。

---

## 一、hack2hire · Google

### 1.1 非 LeetCode 原创题（Top 10）

轮次分布：Onsite 4，Screening 3，OA 3

| # | 题目 | 轮次 | 考点（推测） | 相关 LC 题 | 映射把握 |
| --- | --- | --- | --- | --- | --- |
| 1 | Windowed Average excluding Largest K | Screening | 滑动窗口 + 有序集合 / 双堆 | [1825. Finding MK Average](https://leetcode.com/problems/finding-mk-average/)<br>[480. Sliding Window Median](https://leetcode.com/problems/sliding-window-median/)<br>[346. Moving Average from Data Stream](https://leetcode.com/problems/moving-average-from-data-stream/) | 高 |
| 2 | Highway Checkpoint | Onsite | 区间 / 调度 / 堆（检查点按路序 0..m-1） | [1094. Car Pooling](https://leetcode.com/problems/car-pooling/)<br>[871. Minimum Number of Refueling Stops](https://leetcode.com/problems/minimum-number-of-refueling-stops/)<br>[253. Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) | 中 |
| 3 | Max Fly Distance | Onsite | 题面未公开，推测为贪心 / 堆（按距离 + 资源约束） | [871. Minimum Number of Refueling Stops](https://leetcode.com/problems/minimum-number-of-refueling-stops/)<br>[1642. Furthest Building You Can Reach](https://leetcode.com/problems/furthest-building-you-can-reach/) | 低 |
| 4 | Subarray-First Iterator | Screening | 迭代器设计 | [251. Flatten 2D Vector](https://leetcode.com/problems/flatten-2d-vector/)<br>[281. Zigzag Iterator](https://leetcode.com/problems/zigzag-iterator/)<br>[341. Flatten Nested List Iterator](https://leetcode.com/problems/flatten-nested-list-iterator/) | 中 |
| 5 | Max Sum Between Leaf Nodes | OA | 树形 DP（叶到叶路径和） | [124. Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/)<br>[543. Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) | 高 |
| 6 | Employee Shift Timeline Table | Onsite | 扫描线 / 区间切分 | [1943. Describe the Painting](https://leetcode.com/problems/describe-the-painting/)<br>[759. Employee Free Time](https://leetcode.com/problems/employee-free-time/)<br>[218. The Skyline Problem](https://leetcode.com/problems/the-skyline-problem/) | 中 |
| 7 | Cake Order Fulfillment Check | OA | 推测为调度可行性（截止时间 + 贪心 / 堆） | [630. Course Schedule III](https://leetcode.com/problems/course-schedule-iii/)<br>[1353. Maximum Number of Events That Can Be Attended](https://leetcode.com/problems/maximum-number-of-events-that-can-be-attended/) | 低 |
| 8 | Dual Car Destinations | OA | 图最短路（多次 Dijkstra 求汇合点） | [2203. Minimum Weighted Subgraph With the Required Paths](https://leetcode.com/problems/minimum-weighted-subgraph-with-the-required-paths/)<br>[743. Network Delay Time](https://leetcode.com/problems/network-delay-time/) | 中 |
| 9 | Date Validator | Onsite | 字符串解析 / 边界校验 | [1154. Day of the Year](https://leetcode.com/problems/day-of-the-year/)<br>[468. Validate IP Address](https://leetcode.com/problems/validate-ip-address/)<br>[65. Valid Number](https://leetcode.com/problems/valid-number/) | 中 |
| 10 | Keyboard Jump Challenge | Screening | 键盘坐标 / 模拟 / DP | [1165. Single-Row Keyboard](https://leetcode.com/problems/single-row-keyboard/)<br>[1138. Alphabet Board Path](https://leetcode.com/problems/alphabet-board-path/)<br>[1320. Minimum Distance to Type a Word Using Two Fingers](https://leetcode.com/problems/minimum-distance-to-type-a-word-using-two-fingers/) | 低-中 |

题面在付费墙后，“相关 LC 题”是根据题名和公开摘要推断的。“低”把握的几道拿到原题后要再核对。

### 1.2 hack2hire 列出的 Google 高频 LC 题（27 道）

难度：Easy 10 / Medium 11 / Hard 6

| 分类 | 数量 | 题目 | 也在 LC 30 天榜？ |
| --- | --- | --- | --- |
| 数组 / 哈希 / 排序 | 4 | [806. Number of Lines To Write String](https://leetcode.com/problems/number-of-lines-to-write-string/) (Easy)<br>[349. Intersection of Two Arrays](https://leetcode.com/problems/intersection-of-two-arrays/) (Easy)<br>[1800. Maximum Ascending Subarray Sum](https://leetcode.com/problems/maximum-ascending-subarray-sum/) (Easy)<br>[189. Rotate Array](https://leetcode.com/problems/rotate-array/) (Medium) | —<br>✅<br>—<br>✅ |
| 双指针 | 6 | [88. Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/) (Easy)<br>[15. 3Sum](https://leetcode.com/problems/3sum/) (Medium)<br>[283. Move Zeroes](https://leetcode.com/problems/move-zeroes/) (Easy)<br>[27. Remove Element](https://leetcode.com/problems/remove-element/) (Easy)<br>[26. Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) (Easy)<br>[167. Two Sum II - Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) (Medium) | ✅<br>✅<br>✅<br>—<br>✅<br>✅ |
| 栈 / 单调栈 | 2 | [224. Basic Calculator](https://leetcode.com/problems/basic-calculator/) (Hard)<br>[772. Basic Calculator III](https://leetcode.com/problems/basic-calculator-iii/) (Hard) | —<br>— |
| 链表 | 1 | [2. Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) (Medium) | ✅ |
| 图 (BFS/DFS/拓扑/最短路) | 1 | [200. Number of Islands](https://leetcode.com/problems/number-of-islands/) (Medium) | ✅ |
| 回溯 | 1 | [22. Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) (Medium) | ✅ |
| 动态规划 | 2 | [312. Burst Balloons](https://leetcode.com/problems/burst-balloons/) (Hard)<br>[198. House Robber](https://leetcode.com/problems/house-robber/) (Medium) | ✅<br>✅ |
| 贪心 / 区间 | 1 | [56. Merge Intervals](https://leetcode.com/problems/merge-intervals/) (Medium) | ✅ |
| 设计题 | 1 | [1825. Finding MK Average](https://leetcode.com/problems/finding-mk-average/) (Hard) | — |
| 数学 / 位运算 | 4 | [9. Palindrome Number](https://leetcode.com/problems/palindrome-number/) (Easy)<br>[398. Random Pick Index](https://leetcode.com/problems/random-pick-index/) (Medium)<br>[2354. Number of Excellent Pairs](https://leetcode.com/problems/number-of-excellent-pairs/) (Hard)<br>[136. Single Number](https://leetcode.com/problems/single-number/) (Easy) | ✅<br>—<br>—<br>✅ |
| 字符串 | 4 | [68. Text Justification](https://leetcode.com/problems/text-justification/) (Hard)<br>[5. Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/) (Medium)<br>[151. Reverse Words in a String](https://leetcode.com/problems/reverse-words-in-a-string/) (Medium)<br>[28. Find the Index of the First Occurrence in a String](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/) (Easy) | —<br>✅<br>—<br>✅ |

这 27 道里有 **17 道** 同时出现在 LC 30 天榜（2026-08-16 快照）：88、9、2、15、283、22、5、26、312、198、349、56、200、136、167、189、28。

---

## 二、LeetCode · Google · 最近 30 天

### 2.1 总览

| 难度 | 数量 | 占比 |
| --- | --- | --- |
| Easy | 72 | 39.3% |
| Medium | 86 | 47.0% |
| Hard | 25 | 13.7% |
| **合计** | **183** | 100% |

频率分档（LC 给的相对频率，最高 100）：

| 频率 | 题数 |
| --- | --- |
| ≥ 60 | 12 |
| 50 – 59.9 | 26 |
| 40 – 49.9 | 37 |
| 30 – 39.9 | 40 |
| < 30 | 68 |

### 2.2 按考点分类（每题只归一个主类）

| 分类 | 题数 | Easy | Medium | Hard |
| --- | --- | --- | --- | --- |
| 数组 / 哈希 / 排序 | 22 | 15 | 6 | 1 |
| 数学 / 位运算 | 18 | 12 | 4 | 2 |
| 双指针 | 16 | 8 | 7 | 1 |
| 二分查找 | 13 | 3 | 7 | 3 |
| 链表 | 12 | 6 | 6 | 0 |
| 动态规划 | 12 | 1 | 8 | 3 |
| 栈 / 单调栈 | 10 | 4 | 4 | 2 |
| 贪心 / 区间 | 10 | 3 | 7 | 0 |
| 滑动窗口 | 9 | 3 | 5 | 1 |
| 二叉树 | 9 | 5 | 4 | 0 |
| 图 (BFS/DFS/拓扑/最短路) | 8 | 0 | 5 | 3 |
| 字符串 | 8 | 3 | 5 | 0 |
| 前缀和 / 差分 | 7 | 2 | 5 | 0 |
| 高级结构 (Trie/线段树/倍增/折半) | 7 | 0 | 2 | 5 |
| 回溯 | 5 | 0 | 4 | 1 |
| 设计题 | 5 | 2 | 2 | 1 |
| 博弈 DP (Stone Game 系列) | 4 | 0 | 3 | 1 |
| SQL | 4 | 4 | 0 | 0 |
| 堆 | 2 | 0 | 1 | 1 |
| 新题·暂无标签 | 2 | 1 | 1 | 0 |
| **合计** | **183** | 72 | 86 | 25 |

LC 官方 Topic 标签 Top 15（一题多标签，所以总数大于题数）：

| Topic | 题数 |
| --- | --- |
| Array | 99 |
| Hash Table | 39 |
| String | 39 |
| Two Pointers | 32 |
| Math | 29 |
| Sorting | 28 |
| Dynamic Programming | 28 |
| Binary Search | 24 |
| Linked List | 14 |
| Stack | 14 |
| Breadth-First Search | 14 |
| Depth-First Search | 13 |
| Greedy | 11 |
| Prefix Sum | 11 |
| Recursion | 10 |

### 2.3 频率 Top 20

| 排名 | 题目 | 难度 | 频率 | 分类 |
| --- | --- | --- | --- | --- |
| 1 | [1. Two Sum](https://leetcode.com/problems/two-sum/) | Easy | 100.0 | 数组 / 哈希 / 排序 |
| 2 | [2. Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) | Medium | 72.8 | 链表 |
| 3 | [15. 3Sum](https://leetcode.com/problems/3sum/) | Medium | 66.8 | 双指针 |
| 4 | [121. Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | Easy | 65.3 | 贪心 / 区间 |
| 5 | [9. Palindrome Number](https://leetcode.com/problems/palindrome-number/) | Easy | 63.7 | 数学 / 位运算 |
| 6 | [3. Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | Medium | 63.7 | 滑动窗口 |
| 7 | [42. Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) | Hard | 63.7 | 双指针 |
| 8 | [4. Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/) | Hard | 62.0 | 二分查找 |
| 9 | [26. Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) | Easy | 62.0 | 双指针 |
| 10 | [14. Longest Common Prefix](https://leetcode.com/problems/longest-common-prefix/) | Easy | 62.0 | 字符串 |
| 11 | [11. Container With Most Water](https://leetcode.com/problems/container-with-most-water/) | Medium | 62.0 | 双指针 |
| 12 | [7. Reverse Integer](https://leetcode.com/problems/reverse-integer/) | Medium | 60.2 | 数学 / 位运算 |
| 13 | [169. Majority Element](https://leetcode.com/problems/majority-element/) | Easy | 58.1 | 数组 / 哈希 / 排序 |
| 14 | [175. Combine Two Tables](https://leetcode.com/problems/combine-two-tables/) | Easy | 58.1 | SQL |
| 15 | [1929. Concatenation of Array](https://leetcode.com/problems/concatenation-of-array/) | Easy | 55.8 | 数组 / 哈希 / 排序 |
| 16 | [421. Maximum XOR of Two Numbers in an Array](https://leetcode.com/problems/maximum-xor-of-two-numbers-in-an-array/) | Medium | 55.8 | 高级结构 (Trie/线段树/倍增/折半) |
| 17 | [128. Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) | Medium | 53.2 | 数组 / 哈希 / 排序 |
| 18 | [410. Split Array Largest Sum](https://leetcode.com/problems/split-array-largest-sum/) | Hard | 53.2 | 二分查找 |
| 19 | [242. Valid Anagram](https://leetcode.com/problems/valid-anagram/) | Easy | 53.2 | 数组 / 哈希 / 排序 |
| 20 | [283. Move Zeroes](https://leetcode.com/problems/move-zeroes/) | Easy | 53.2 | 双指针 |

### 2.4 分类完整列表

#### 数组 / 哈希 / 排序（22）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [1. Two Sum](https://leetcode.com/problems/two-sum/) | Easy | 100.0 |
| [169. Majority Element](https://leetcode.com/problems/majority-element/) | Easy | 58.1 |
| [1929. Concatenation of Array](https://leetcode.com/problems/concatenation-of-array/) | Easy | 55.8 |
| [128. Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) | Medium | 53.2 |
| [242. Valid Anagram](https://leetcode.com/problems/valid-anagram/) | Easy | 53.2 |
| [49. Group Anagrams](https://leetcode.com/problems/group-anagrams/) | Medium | 50.2 |
| [217. Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) | Easy | 50.2 |
| [1464. Maximum Product of Two Elements in an Array](https://leetcode.com/problems/maximum-product-of-two-elements-in-an-array/) | Easy | 50.2 |
| [3731. Find Missing Elements](https://leetcode.com/problems/find-missing-elements/) | Easy | 50.2 |
| [189. Rotate Array](https://leetcode.com/problems/rotate-array/) | Medium | 46.6 |
| [41. First Missing Positive](https://leetcode.com/problems/first-missing-positive/) | Hard | 42.3 |
| [349. Intersection of Two Arrays](https://leetcode.com/problems/intersection-of-two-arrays/) | Easy | 42.3 |
| [2996. Smallest Missing Integer Greater Than Sequential Prefix Sum](https://leetcode.com/problems/smallest-missing-integer-greater-than-sequential-prefix-sum/) | Easy | 42.3 |
| [912. Sort an Array](https://leetcode.com/problems/sort-an-array/) | Medium | 36.7 |
| [1752. Check if Array Is Sorted and Rotated](https://leetcode.com/problems/check-if-array-is-sorted-and-rotated/) | Easy | 36.7 |
| [1260. Shift 2D Grid](https://leetcode.com/problems/shift-2d-grid/) | Easy | 36.7 |
| [205. Isomorphic Strings](https://leetcode.com/problems/isomorphic-strings/) | Easy | 36.7 |
| [54. Spiral Matrix](https://leetcode.com/problems/spiral-matrix/) | Medium | 36.7 |
| [485. Max Consecutive Ones](https://leetcode.com/problems/max-consecutive-ones/) | Easy | 29.0 |
| [274. H-Index](https://leetcode.com/problems/h-index/) | Medium | 29.0 |
| [2965. Find Missing and Repeated Values](https://leetcode.com/problems/find-missing-and-repeated-values/) | Easy | 29.0 |
| [1672. Richest Customer Wealth](https://leetcode.com/problems/richest-customer-wealth/) | Easy | 29.0 |

#### 数学 / 位运算（18）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [9. Palindrome Number](https://leetcode.com/problems/palindrome-number/) | Easy | 63.7 |
| [7. Reverse Integer](https://leetcode.com/problems/reverse-integer/) | Medium | 60.2 |
| [628. Maximum Product of Three Numbers](https://leetcode.com/problems/maximum-product-of-three-numbers/) | Easy | 53.2 |
| [231. Power of Two](https://leetcode.com/problems/power-of-two/) | Easy | 50.2 |
| [3345. Smallest Divisible Digit Product I](https://leetcode.com/problems/smallest-divisible-digit-product-i/) | Easy | 50.2 |
| [66. Plus One](https://leetcode.com/problems/plus-one/) | Easy | 46.6 |
| [2235. Add Two Integers](https://leetcode.com/problems/add-two-integers/) | Easy | 46.6 |
| [202. Happy Number](https://leetcode.com/problems/happy-number/) | Easy | 42.3 |
| [50. Pow(x, n)](https://leetcode.com/problems/powx-n/) | Medium | 36.7 |
| [268. Missing Number](https://leetcode.com/problems/missing-number/) | Easy | 36.7 |
| [3536. Maximum Product of Two Digits](https://leetcode.com/problems/maximum-product-of-two-digits/) | Easy | 36.7 |
| [389. Find the Difference](https://leetcode.com/problems/find-the-difference/) | Easy | 36.7 |
| [136. Single Number](https://leetcode.com/problems/single-number/) | Easy | 29.0 |
| [3518. Smallest Palindromic Rearrangement II](https://leetcode.com/problems/smallest-palindromic-rearrangement-ii/) | Hard | 29.0 |
| [3348. Smallest Divisible Digit Product II](https://leetcode.com/problems/smallest-divisible-digit-product-ii/) | Hard | 29.0 |
| [204. Count Primes](https://leetcode.com/problems/count-primes/) | Medium | 29.0 |
| [29. Divide Two Integers](https://leetcode.com/problems/divide-two-integers/) | Medium | 29.0 |
| [1518. Water Bottles](https://leetcode.com/problems/water-bottles/) | Easy | 29.0 |

#### 双指针（16）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [15. 3Sum](https://leetcode.com/problems/3sum/) | Medium | 66.8 |
| [42. Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) | Hard | 63.7 |
| [26. Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) | Easy | 62.0 |
| [11. Container With Most Water](https://leetcode.com/problems/container-with-most-water/) | Medium | 62.0 |
| [283. Move Zeroes](https://leetcode.com/problems/move-zeroes/) | Easy | 53.2 |
| [344. Reverse String](https://leetcode.com/problems/reverse-string/) | Easy | 50.2 |
| [18. 4Sum](https://leetcode.com/problems/4sum/) | Medium | 46.6 |
| [16. 3Sum Closest](https://leetcode.com/problems/3sum-closest/) | Medium | 46.6 |
| [167. Two Sum II - Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) | Medium | 46.6 |
| [977. Squares of a Sorted Array](https://leetcode.com/problems/squares-of-a-sorted-array/) | Easy | 42.3 |
| [88. Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/) | Easy | 36.7 |
| [287. Find the Duplicate Number](https://leetcode.com/problems/find-the-duplicate-number/) | Medium | 36.7 |
| [1768. Merge Strings Alternately](https://leetcode.com/problems/merge-strings-alternately/) | Easy | 29.0 |
| [125. Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) | Easy | 29.0 |
| [1089. Duplicate Zeros](https://leetcode.com/problems/duplicate-zeros/) | Easy | 29.0 |
| [80. Remove Duplicates from Sorted Array II](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/) | Medium | 29.0 |

#### 二分查找（13）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [4. Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/) | Hard | 62.0 |
| [410. Split Array Largest Sum](https://leetcode.com/problems/split-array-largest-sum/) | Hard | 53.2 |
| [704. Binary Search](https://leetcode.com/problems/binary-search/) | Easy | 53.2 |
| [35. Search Insert Position](https://leetcode.com/problems/search-insert-position/) | Easy | 50.2 |
| [33. Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) | Medium | 36.7 |
| [69. Sqrt(x)](https://leetcode.com/problems/sqrtx/) | Easy | 36.7 |
| [34. Find First and Last Position of Element in Sorted Array](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/) | Medium | 36.7 |
| [162. Find Peak Element](https://leetcode.com/problems/find-peak-element/) | Medium | 29.0 |
| [1482. Minimum Number of Days to Make m Bouquets](https://leetcode.com/problems/minimum-number-of-days-to-make-m-bouquets/) | Medium | 29.0 |
| [875. Koko Eating Bananas](https://leetcode.com/problems/koko-eating-bananas/) | Medium | 29.0 |
| [153. Find Minimum in Rotated Sorted Array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/) | Medium | 29.0 |
| [154. Find Minimum in Rotated Sorted Array II](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array-ii/) | Hard | 29.0 |
| [540. Single Element in a Sorted Array](https://leetcode.com/problems/single-element-in-a-sorted-array/) | Medium | 29.0 |

#### 链表（12）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [2. Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) | Medium | 72.8 |
| [206. Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/) | Easy | 50.2 |
| [876. Middle of the Linked List](https://leetcode.com/problems/middle-of-the-linked-list/) | Easy | 50.2 |
| [234. Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/) | Easy | 46.6 |
| [83. Remove Duplicates from Sorted List](https://leetcode.com/problems/remove-duplicates-from-sorted-list/) | Easy | 42.3 |
| [143. Reorder List](https://leetcode.com/problems/reorder-list/) | Medium | 42.3 |
| [148. Sort List](https://leetcode.com/problems/sort-list/) | Medium | 36.7 |
| [21. Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) | Easy | 29.0 |
| [328. Odd Even Linked List](https://leetcode.com/problems/odd-even-linked-list/) | Medium | 29.0 |
| [19. Remove Nth Node From End of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) | Medium | 29.0 |
| [61. Rotate List](https://leetcode.com/problems/rotate-list/) | Medium | 29.0 |
| [141. Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/) | Easy | 29.0 |

#### 动态规划（12）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [198. House Robber](https://leetcode.com/problems/house-robber/) | Medium | 50.2 |
| [70. Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) | Easy | 36.7 |
| [312. Burst Balloons](https://leetcode.com/problems/burst-balloons/) | Hard | 36.7 |
| [322. Coin Change](https://leetcode.com/problems/coin-change/) | Medium | 29.0 |
| [10. Regular Expression Matching](https://leetcode.com/problems/regular-expression-matching/) | Hard | 29.0 |
| [416. Partition Equal Subset Sum](https://leetcode.com/problems/partition-equal-subset-sum/) | Medium | 29.0 |
| [1143. Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/) | Medium | 29.0 |
| [91. Decode Ways](https://leetcode.com/problems/decode-ways/) | Medium | 29.0 |
| [983. Minimum Cost For Tickets](https://leetcode.com/problems/minimum-cost-for-tickets/) | Medium | 29.0 |
| [62. Unique Paths](https://leetcode.com/problems/unique-paths/) | Medium | 29.0 |
| [63. Unique Paths II](https://leetcode.com/problems/unique-paths-ii/) | Medium | 29.0 |
| [174. Dungeon Game](https://leetcode.com/problems/dungeon-game/) | Hard | 29.0 |

#### 栈 / 单调栈（10）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [1081. Smallest Subsequence of Distinct Characters](https://leetcode.com/problems/smallest-subsequence-of-distinct-characters/) | Medium | 46.6 |
| [496. Next Greater Element I](https://leetcode.com/problems/next-greater-element-i/) | Easy | 46.6 |
| [20. Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) | Easy | 42.3 |
| [503. Next Greater Element II](https://leetcode.com/problems/next-greater-element-ii/) | Medium | 36.7 |
| [1944. Number of Visible People in a Queue](https://leetcode.com/problems/number-of-visible-people-in-a-queue/) | Hard | 36.7 |
| [84. Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) | Hard | 29.0 |
| [1047. Remove All Adjacent Duplicates In String](https://leetcode.com/problems/remove-all-adjacent-duplicates-in-string/) | Easy | 29.0 |
| [739. Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) | Medium | 29.0 |
| [232. Implement Queue using Stacks](https://leetcode.com/problems/implement-queue-using-stacks/) | Easy | 29.0 |
| [394. Decode String](https://leetcode.com/problems/decode-string/) | Medium | 29.0 |

#### 贪心 / 区间（10）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [121. Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | Easy | 65.3 |
| [3302. Find the Lexicographically Smallest Valid Sequence](https://leetcode.com/problems/find-the-lexicographically-smallest-valid-sequence/) | Medium | 50.2 |
| [3014. Minimum Number of Pushes to Type Word I](https://leetcode.com/problems/minimum-number-of-pushes-to-type-word-i/) | Easy | 46.6 |
| [122. Best Time to Buy and Sell Stock II](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/) | Medium | 42.3 |
| [45. Jump Game II](https://leetcode.com/problems/jump-game-ii/) | Medium | 36.7 |
| [56. Merge Intervals](https://leetcode.com/problems/merge-intervals/) | Medium | 36.7 |
| [253. Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) | Medium | 36.7 |
| [605. Can Place Flowers](https://leetcode.com/problems/can-place-flowers/) | Easy | 29.0 |
| [57. Insert Interval](https://leetcode.com/problems/insert-interval/) | Medium | 29.0 |
| [435. Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) | Medium | 29.0 |

#### 滑动窗口（9）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [3. Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | Medium | 63.7 |
| [239. Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) | Hard | 50.2 |
| [424. Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/) | Medium | 46.6 |
| [219. Contains Duplicate II](https://leetcode.com/problems/contains-duplicate-ii/) | Easy | 42.3 |
| [643. Maximum Average Subarray I](https://leetcode.com/problems/maximum-average-subarray-i/) | Easy | 36.7 |
| [713. Subarray Product Less Than K](https://leetcode.com/problems/subarray-product-less-than-k/) | Medium | 36.7 |
| [3090. Maximum Length Substring With Two Occurrences](https://leetcode.com/problems/maximum-length-substring-with-two-occurrences/) | Easy | 36.7 |
| [2958. Length of Longest Subarray With at Most K Frequency](https://leetcode.com/problems/length-of-longest-subarray-with-at-most-k-frequency/) | Medium | 29.0 |
| [904. Fruit Into Baskets](https://leetcode.com/problems/fruit-into-baskets/) | Medium | 29.0 |

#### 二叉树（9）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [94. Binary Tree Inorder Traversal](https://leetcode.com/problems/binary-tree-inorder-traversal/) | Easy | 46.6 |
| [104. Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/) | Easy | 42.3 |
| [543. Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) | Easy | 36.7 |
| [236. Lowest Common Ancestor of a Binary Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/) | Medium | 36.7 |
| [2096. Step-By-Step Directions From a Binary Tree Node to Another](https://leetcode.com/problems/step-by-step-directions-from-a-binary-tree-node-to-another/) | Medium | 29.0 |
| [101. Symmetric Tree](https://leetcode.com/problems/symmetric-tree/) | Easy | 29.0 |
| [226. Invert Binary Tree](https://leetcode.com/problems/invert-binary-tree/) | Easy | 29.0 |
| [222. Count Complete Tree Nodes](https://leetcode.com/problems/count-complete-tree-nodes/) | Medium | 29.0 |
| [103. Binary Tree Zigzag Level Order Traversal](https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/) | Medium | 29.0 |

#### 图 (BFS/DFS/拓扑/最短路)（8）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [200. Number of Islands](https://leetcode.com/problems/number-of-islands/) | Medium | 50.2 |
| [994. Rotting Oranges](https://leetcode.com/problems/rotting-oranges/) | Medium | 42.3 |
| [2045. Second Minimum Time to Reach Destination](https://leetcode.com/problems/second-minimum-time-to-reach-destination/) | Hard | 36.7 |
| [310. Minimum Height Trees](https://leetcode.com/problems/minimum-height-trees/) | Medium | 29.0 |
| [3310. Remove Methods From Project](https://leetcode.com/problems/remove-methods-from-project/) | Medium | 29.0 |
| [127. Word Ladder](https://leetcode.com/problems/word-ladder/) | Hard | 29.0 |
| [207. Course Schedule](https://leetcode.com/problems/course-schedule/) | Medium | 29.0 |
| [815. Bus Routes](https://leetcode.com/problems/bus-routes/) | Hard | 29.0 |

#### 字符串（8）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [14. Longest Common Prefix](https://leetcode.com/problems/longest-common-prefix/) | Easy | 62.0 |
| [13. Roman to Integer](https://leetcode.com/problems/roman-to-integer/) | Easy | 36.7 |
| [5. Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/) | Medium | 36.7 |
| [28. Find the Index of the First Occurrence in a String](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/) | Easy | 36.7 |
| [6. Zigzag Conversion](https://leetcode.com/problems/zigzag-conversion/) | Medium | 36.7 |
| [3499. Maximize Active Section with Trade I](https://leetcode.com/problems/maximize-active-section-with-trade-i/) | Medium | 36.7 |
| [3517. Smallest Palindromic Rearrangement I](https://leetcode.com/problems/smallest-palindromic-rearrangement-i/) | Medium | 36.7 |
| [12. Integer to Roman](https://leetcode.com/problems/integer-to-roman/) | Medium | 29.0 |

#### 前缀和 / 差分（7）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [560. Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) | Medium | 50.2 |
| [1480. Running Sum of 1d Array](https://leetcode.com/problems/running-sum-of-1d-array/) | Easy | 46.6 |
| [238. Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/) | Medium | 42.3 |
| [303. Range Sum Query - Immutable](https://leetcode.com/problems/range-sum-query-immutable/) | Easy | 42.3 |
| [1094. Car Pooling](https://leetcode.com/problems/car-pooling/) | Medium | 29.0 |
| [974. Subarray Sums Divisible by K](https://leetcode.com/problems/subarray-sums-divisible-by-k/) | Medium | 29.0 |
| [3026. Maximum Good Subarray Sum](https://leetcode.com/problems/maximum-good-subarray-sum/) | Medium | 29.0 |

#### 高级结构 (Trie/线段树/倍增/折半)（7）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [421. Maximum XOR of Two Numbers in an Array](https://leetcode.com/problems/maximum-xor-of-two-numbers-in-an-array/) | Medium | 55.8 |
| [3501. Maximize Active Section with Trade II](https://leetcode.com/problems/maximize-active-section-with-trade-ii/) | Hard | 42.3 |
| [493. Reverse Pairs](https://leetcode.com/problems/reverse-pairs/) | Hard | 36.7 |
| [2035. Partition Array Into Two Arrays to Minimize Sum Difference](https://leetcode.com/problems/partition-array-into-two-arrays-to-minimize-sum-difference/) | Hard | 29.0 |
| [208. Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/) | Medium | 29.0 |
| [2213. Longest Substring of One Repeating Character](https://leetcode.com/problems/longest-substring-of-one-repeating-character/) | Hard | 29.0 |
| [1483. Kth Ancestor of a Tree Node](https://leetcode.com/problems/kth-ancestor-of-a-tree-node/) | Hard | 29.0 |

#### 回溯（5）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [22. Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) | Medium | 46.6 |
| [17. Letter Combinations of a Phone Number](https://leetcode.com/problems/letter-combinations-of-a-phone-number/) | Medium | 46.6 |
| [51. N-Queens](https://leetcode.com/problems/n-queens/) | Hard | 36.7 |
| [131. Palindrome Partitioning](https://leetcode.com/problems/palindrome-partitioning/) | Medium | 29.0 |
| [79. Word Search](https://leetcode.com/problems/word-search/) | Medium | 29.0 |

#### 设计题（5）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [146. LRU Cache](https://leetcode.com/problems/lru-cache/) | Medium | 36.7 |
| [933. Number of Recent Calls](https://leetcode.com/problems/number-of-recent-calls/) | Easy | 36.7 |
| [359. Logger Rate Limiter](https://leetcode.com/problems/logger-rate-limiter/) | Easy | 36.7 |
| [460. LFU Cache](https://leetcode.com/problems/lfu-cache/) | Hard | 29.0 |
| [981. Time Based Key-Value Store](https://leetcode.com/problems/time-based-key-value-store/) | Medium | 29.0 |

#### 博弈 DP (Stone Game 系列)（4）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [877. Stone Game](https://leetcode.com/problems/stone-game/) | Medium | 50.2 |
| [486. Predict the Winner](https://leetcode.com/problems/predict-the-winner/) | Medium | 46.6 |
| [1406. Stone Game III](https://leetcode.com/problems/stone-game-iii/) | Hard | 42.3 |
| [1140. Stone Game II](https://leetcode.com/problems/stone-game-ii/) | Medium | 42.3 |

#### SQL（4）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [175. Combine Two Tables](https://leetcode.com/problems/combine-two-tables/) | Easy | 58.1 |
| [1757. Recyclable and Low Fat Products](https://leetcode.com/problems/recyclable-and-low-fat-products/) | Easy | 46.6 |
| [181. Employees Earning More Than Their Managers](https://leetcode.com/problems/employees-earning-more-than-their-managers/) | Easy | 42.3 |
| [584. Find Customer Referee](https://leetcode.com/problems/find-customer-referee/) | Easy | 42.3 |

#### 堆（2）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [347. Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) | Medium | 42.3 |
| [295. Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) | Hard | 29.0 |

#### 新题·暂无标签（2）

| 题目 | 难度 | 频率 |
| --- | --- | --- |
| [Count Valid Sequences](https://leetcode.com/problems/count-valid-sequences/) | Medium | 36.7 |
| [Unique Middle Element](https://leetcode.com/problems/unique-middle-element/) | Easy | 29.0 |

---

## 三、说明

- LC 的“30 天”是滚动窗口。另一个镜像 [snehasishroy/leetcode-companywise-interview-questions](https://github.com/snehasishroy/leetcode-companywise-interview-questions) 的 2026-07-12 快照有 201 题，和 08-16 快照只重合 90 题，所以今天的实时榜单还会不一样。
- 分类是按主解法人工归类的，一题只算一类（例如 Trapping Rain Water 归双指针，Car Pooling 归差分）。
- `Count Valid Sequences`、`Unique Middle Element` 是 2026 年的新题，镜像里没有题号和标签，暂归“新题·暂无标签”。
