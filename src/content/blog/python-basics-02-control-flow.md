---
title: 'Python 基础 02：控制流——选择、循环与双指针初探'
description: 'range 的边界、enumerate 与反向遍历、break/continue/循环 else、嵌套循环复杂度，以及第一道真正的算法题：有序数组两数之和（双指针）。'
pubDate: 2026-11-26
tags: ['Python', '学习笔记', '算法']
series: 'Python 基础'
---

> [Python 基础](/series/python-basics/)第 2 篇。上一篇：[变量与数据类型](/blog/python-basics-01-vars-types/)。

## 一、控制流：让程序做选择和重复工作

程序默认从上到下一行一行执行。控制流解决两个问题：

- **选择**：满足条件时执行哪一段代码？（`if / elif / else`）
- **重复**：一段代码执行多少次、什么时候停止？（`for / while`）

### 解读"算法本质上就是'状态 + 控制流'"

这句话的意思是：**任何算法，无论名字多唬人，拆开都是两样东西——**

- **状态**：程序"记住的当前局面"，存在变量里；
- **控制流**：根据状态决定下一步——走哪个分支、推进什么、何时停止。

拿主角们逐个验证：

| 算法 | 状态（记在变量里） | 控制流（if + 循环干什么） |
| --- | --- | --- |
| 数组遍历 | 下标 `i` | 循环推进 `i`，越界即停 |
| 二分查找 | 区间边界 `left, right` | 比较中间值 → if 决定收缩左半还是右半 → 区间空了停 |
| DFS（深度优先） | 一个栈 + 已访问集合 | 取栈顶 → 循环压入未访问邻居 → 栈空停（递归版用系统栈） |
| 动态规划 | DP 表（子问题的答案） | 按依赖顺序循环填表，填完停 |

所以最后那句"数组遍历、二分查找、DFS 和动态规划，最后都会落到条件与循环"说的是：**再复杂的算法，骨架也只是若干个变量（状态）加一堆 if 和循环（控制流）**。

> 💡 学任何新算法，先问两个问题：**它的状态是什么？它怎么推进、怎么终止？**——这两个问题答出来，算法就"会了一半"。

## 二、range：边界与步长

```python
range(start, stop, step)   # 包含 start，不包含 stop（左闭右开，与切片一致！）
```

```python
list(range(5))            # [0, 1, 2, 3, 4]        —— start 默认 0
list(range(2, 6))         # [2, 3, 4, 5]
list(range(0, 10, 2))     # [0, 2, 4, 6, 8]        —— 步长 2
list(range(5, -1, -1))    # [5, 4, 3, 2, 1, 0]     —— 负步长 = 倒着数
```

### 空 range 之谜

```python
list(range(5, 1))       # []
list(range(5, 1, 1))    # []    ← 为什么？
```

把 range 想象成"**从 start 出发，每步跨 step，朝着 stop 的方向走，但不踩到 stop**"：

- `range(5, 1, 1)`：步长是**正**的（朝大数方向走），但 stop=1 在 start=5 的**反方向**——起步就背道而驰，一步都迈不出去 → 空；
- `range(5, 1)`：step 默认 1，同上 → 空；
- `range(5, -1, -1)`：步长**负**（朝小数方向走），stop=-1 在正前方 → 一路倒数到 0 ✓。

**口诀：步长是方向，方向必须对着 stop 走；背道而驰 → 空。**（正向遍历写出 `range(5, 1)` 十有八九是把"从 5 到 1"想当然写了，正确写法是 `range(5, 0, -1)`。）

## 三、遍历的正确姿势

```python
nums = [10, 20, 30]

# ① 只需要值（首选，最 Pythonic）
for value in nums: ...

# ② 只需要下标
for i in range(len(nums)): ...

# ③ 下标和值都要 → enumerate（首选，别写 range(len()) 再取下标！）
for i, value in enumerate(nums):
    print(i, value)          # 0 10 / 1 20 / 2 30
for i, value in enumerate(nums, start=1):   # 下标从 1 开始数
    print(i, value)          # 1 10 / 2 20 / 3 30

# ④ 反向遍历值
for value in reversed(nums): ...

# ⑤ 反向遍历下标
for i in range(len(nums) - 1, -1, -1):
    print(i, nums[i])        # 2 30 / 1 20 / 0 10
```

⑤ 的**停止值必须是 `-1`**——range 不含 stop：写 0 会漏掉下标 0，写 -1 才"想包含 0"。这正是左闭右开在倒着走时的体现。

**顺手记 zip**（多序列同步遍历，刷题常配 dict）：

```python
for name, score in zip(["tom", "jerry"], [90, 85]):
    print(name, score)       # tom 90 / jerry 85
```

> ⚠️ **遍历时不要增删正在遍历的列表**：删除会让后面的元素"前移"，循环却照旧跳一格 → 跳过元素。需要过滤时用推导式 `new = [x for x in nums if x != target]`；必须原地删就倒着遍历（`⑤` 的写法，删除不影响尚未访问的前面部分）。

## 四、break、continue 与循环的 else

```python
# break：立刻跳出整个循环
for x in nums:
    if x < 0:
        break          # 碰到第一个负数就收工

# continue：跳过本轮剩余语句，直接进入下一轮
for x in nums:
    if x < 0:
        continue       # 负数跳过不处理
    process(x)
```

**循环的 else**——Python 的独门写法，最容易望文生义的地方：

```python
for n in range(2, 50):
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            break          # 找到因数，提前结束内层循环
    else:                  # ← 内层循环"没被 break 打断、正常跑完"才执行
        print(n, "是素数")
```

- `else` 跟在 `for`/`while` 后面（**不是** if 的 else）；
- 触发条件：循环**自然耗尽**（一次 break 都没遇到）；
- 天然表达"**找没找到**"：找到 → break → 不进 else；没找到 → 跑完 → 进 else。

不用 for-else 的等价写法（用旗标变量）：

```python
found = False
for d in range(2, int(n ** 0.5) + 1):
    if n % d == 0:
        found = True
        break
if not found:
    print(n, "是素数")
```

for-else 就是这段的语法糖——更短，但可读性见仁见智，两种都要看得懂。

## 五、嵌套循环与复杂度

**嵌套相乘，前后相加**：

```python
for i in range(n):
    for j in range(m):
        process(i, j)       # 内层体执行 n × m 次 → O(n·m)
```

```python
for value in nums:          # O(n)
    process(value)

for value in nums:          # O(n)
    process_again(value)
# 两个循环前后排：总计 O(n + n) = O(n)，不是 O(n²)！
```

体感一下量级（每秒约 10⁷~10⁸ 次简单运算）：

| n | O(n) | O(n²) |
| --- | --- | --- |
| 10³ | 瞬间 | ~10⁶，依然瞬间 |
| 10⁵ | ~毫秒 | ~10¹⁰，**十几分钟** |
| 10⁶ | ~10 毫秒 | ~10¹²，不可接受 |

所以 LeetCode 看到 n ≤ 10⁵ 的题，O(n²) 大概率超时——要么 O(n log n)（排序/二分），要么 O(n)（哈希/双指针，见下一节）。

另一个经典模式（枚举所有**对**）：`for i: for j in range(i+1, n)` 执行 n(n−1)/2 次——仍是 O(n²)，只是少了一半。

## 六、实战：有序数组的两数之和（双指针）

> **题目**（LeetCode 167）：升序数组 `nums` 和目标值 `target`，找出两个数使和恰为 `target`，返回下标。恰好一个解。

**暴力解**：枚举所有对 → 双循环 O(n²)——刚学的复杂度立刻用上了。

**双指针解 O(n)**：一头一尾两个指针，往中间夹：

```python
def two_sum_sorted(nums: list[int], target: int) -> list[int]:
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return [left, right]
        elif s < target:
            left += 1     # 和太小 → 换个更大的左数
        else:
            right -= 1    # 和太大 → 换个更小的右数
    return []
```

**为什么移动指针是安全的**（不会错过解）？拿 `s < target` 说：此刻 `nums[left]` 和数组里**最大的** `nums[right]` 配对都不够——它跟其余任何人配更不够。所以 `nums[left]` 不可能出现在答案里，扔掉它零风险。`s > target` 同理对称。

这也正是第一节那句话的现场演绎：**状态** = `left, right` 两个变量（当前考察的区间）；**控制流** = 一个 while + 三个分支（推进哪个指针、何时停）。

### `while left <= right` 与 `while left < right`：区间定义之争

两种写法对应两种**区间含义**，选哪种取决于"最后剩一个元素时，还算不算候选"：

| 循环条件 | 区间含义 | `left == right` 时 | 适用 |
| --- | --- | --- | --- |
| `left < right` | 至少两个元素（可理解为左闭右开 `(left, right]` 之类） | 立即停止，**单个元素不再考察** | 答案需要**两个不同元素**（两数之和） |
| `left <= right` | 闭区间 `[left, right]` | 还剩一个候选，**再查一次** | 答案可以就是"这一个"（二分查找） |

对照二分查找（用 `<=` 的典型）：

```python
def binary_search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:              # 闭区间 [left, right]：还有元素就没查完
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1                          # 区间收缩为空，确实没有
```

**口诀：还剩最后一个元素时需不需要检查？**要 → `<=`（闭区间）；不要（要成对/成组）→ `<`。写错边界是二分和双指针最著名的 off-by-one 事故来源——想清楚区间含义，比背模板重要。

## 自测小练习

1. `list(range(10, 0, -2))` 是什么？
2. 下标从 1 开始遍历 `nums`，enumerate 怎么写？
3. for-else 的 else 什么时候执行？
4. 双指针两数之和中，为什么 `s < target` 时移动**左**指针是安全的？
5. `for i in range(n): for j in range(i + 1, n):` 的时间复杂度是多少？
6. 二分查找用 `left <= right`，两数之和用 `left < right`，一句话说清为什么不同。

> 答案：① `[10, 8, 6, 4, 2]` ② `for i, x in enumerate(nums, start=1):`（或 `enumerate(nums, 1)`）③ 循环没被 break 打断、自然跑完时 ④ 有序数组里 `nums[left]` 与最大的 `nums[right]` 配对仍不够小，它与其他任何数配更不够——不可能在答案里，扔掉零风险 ⑤ 执行 n(n−1)/2 次 → O(n²) ⑥ 二分的答案可以是"最后那一个元素"（闭区间 `[l, r]`，要检查到底）；两数之和需要两个不同元素，`left == right` 时无意义（立即停）

## 下一篇

[《Python 基础 03：函数——参数、作用域与递归》](/blog/python-basics-03-functions/)已发布。容器进阶（浅拷贝/深拷贝、推导式）与第一篇 LeetCode 正式题解排队中。

---

*新笔记放 `src/content/blog/`，frontmatter 带 `series: 'Python 基础'`，[专栏页](/series/python-basics/)自动收录。*
