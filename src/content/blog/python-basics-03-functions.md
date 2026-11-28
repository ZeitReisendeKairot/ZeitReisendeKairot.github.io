---
title: 'Python 基础 03：函数——参数、作用域与递归'
description: '默认参数的坑、传的是"对象引用"、LEGB 作用域与 nonlocal、lambda 与 key 排序（三个灵魂拷问）、递归与调用栈——刷题前的最后一块地基。'
pubDate: 2026-11-28
tags: ['Python', '学习笔记', '算法']
series: 'Python 基础'
---

> [Python 基础](/series/python-basics/)第 3 篇。上篇：[控制流](/blog/python-basics-02-control-flow/)。本篇仍是"以刷题为目的地"的基础——每个知识点都标了它在算法题里的出场位置。

## 一、函数的四个部分

```python
def divide(a, b):                 # ① 定义头：def 函数名(形参):
    """两数相除；除数为 0 时返回 None。"""   # ② 文档字符串（可选，强烈推荐写）
    if b == 0:                     # ③ 函数体：缩进的代码块（逻辑在这里）
        return None
    return a / b                   # ④ 返回值：return 交给调用者

result = divide(10, 3)             # 调用：函数名(实参) → 3.333...
```

| 部分 | 说明 |
| --- | --- |
| ① 定义头 | `def` + 名字 + 圆括号里的**形参**（占位的名字） |
| ② 文档字符串 | 第一行的字符串，`help(divide)` 能看到 |
| ③ 函数体 | 一段有名字、可反复调用的逻辑 |
| ④ 返回值 | `return` 把结果交出去；**不写 return 或裸 return → 返回 None** |

两个细节：

- `return a, b` 其实返回**一个元组** `(a, b)`——所以 `low, high = divide_pair(x)` 能直接"解包"（02 篇的 divmod 就是这么返回的）；
- **函数名本身也是变量**（可以赋值、可以当参数传递）——这个事实是第五节 `key=sort_key` 的伏笔，先记住。

## 二、默认参数：顺序规则与"可变默认值"这个大坑

规则一：**默认参数必须写在非默认参数后面**，否则 `SyntaxError`：

```python
def f(a=1, b): ...        # SyntaxError: 默认参数不能放在必选参数前
def f(a, b=1): ...        # ✓
```

规则二（经典面试坑）：**不要把可变对象（list/dict/set）设为默认值**：

```python
def add_item(item, items=[]):    # 坑！
    items.append(item)
    return items

add_item(1)      # [1]
add_item(2)      # [1, 2] ←！！预期 [2]，却"记住"了上次的结果
```

**原因**：默认值在 `def` 语句**执行的那一刻创建一次**，之后**所有调用共享同一个列表对象**——用 01 篇的话说，每次调用都把"items 这个名字"贴到**同一个**列表上（`add_item(1)` 和 `add_item(2)` 操作的是同一块内存）。

正确写法（None 哨兵模式）：

```python
def add_item(item, items=None):
    if items is None:             # 01 篇的 is None 在这里上岗
        items = []                # 每次调用现建新列表
    items.append(item)
    return items

add_item(1)   # [1]
add_item(2)   # [2] ✓
```

**原则：默认值只用不可变对象**（None、数字、字符串、元组）。

## 三、参数传递：传的是"对象引用"

Python 的参数传递既不是"传值"也不是"传引用"，准确说法是**传对象引用**：调用时，把形参这个名字**贴到实参所指向的同一个对象上**。后果取决于对象**可不可变**（01 篇的分类在此封神）：

```python
def change_number(number):
    number += 1          # 整数不可变：+= 只能"创建新对象+把标签挪过去"
                         # → 外部毫无感觉

def change_list(nums):
    nums.append(99)      # 列表可变：原地修改同一个对象
                         # → 外部可见！

x = 10
values = [1, 2]
change_number(x)         # x 仍是 10
change_list(values)      # values 变成 [1, 2, 99]
```

一对孪生对照（01 篇陷阱 A6 的函数版）：

```python
def mutate(nums):
    nums += [4]          # 原地扩展：外部可见

def rebind(nums):
    nums = nums + [4]    # 创建新列表、把形参标签贴到新列表上：外部不可见
```

**刷题指南**：

- 题目要求"**原地**修改数组"（双指针、去重类）→ 直接改，还能省内存；
- 不想污染调用者的输入 → 先复制：`copied = nums[:]`（或 `list(nums)`；嵌套结构用 `copy.deepcopy`）。

## 四、作用域：局部、global、nonlocal 与闭包

函数内部定义的变量默认是**局部变量**——只活在这次调用里，和外部的同名变量**互不相干**：

```python
count = 10

def work():
    count = 3            # 在函数内部新建了一个局部变量 count
    return count

work()                   # 3
count                    # 10 —— 全局的 count 毫发无伤
```

**为什么赋值总是"新建局部变量"**？Python 的规则：函数体内出现**赋值**（`count = 3`、`total += 1` 都算）→ 这个名字默认被视为局部。想改外层的变量，必须显式声明：

- `global count`：我要改**模块顶层**的变量（尽量少用——全局状态是测试的天敌）；
- `nonlocal total`：我要改**外层函数**的变量（闭包场景）。

递归和回溯里常见用**闭包**保存答案：

```python
def tree_sum(root):
    total = 0                     # 外层函数的变量

    def dfs(node):
        nonlocal total            # 不写这行：total += 1 会在 dfs 内新建局部变量
        if node is None:          # 然后报 UnboundLocalError（还没赋值就使用）
            return
        total += node.val         # ✓ 声明后改的是外层的 total
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    return total
```

**优先级建议：能用返回值表达，就不用 global / nonlocal**——无副作用的函数最容易测试、最难写错。第七节会给出同一道题的两种实现对照。

## 五、Lambda 与 key 函数

### 先回答三个灵魂拷问

**问题 1：为什么不能直接写 `square = x * x`？**

因为 `x * x` 是一个**表达式**，此刻 `x` 根本没有值——直接执行就是 `NameError`。函数的意义在于把"**怎么算**"打包成**规则**，等调用时才把具体数值代入：

```python
square = lambda x: x * x    # 记下规则："把传进来的东西平方"
square(4)                   # 现在才把 4 代入 → 16
```

类比：`x * x` 是**菜谱**上的一步，`lambda` 把整张菜谱折起来递给别人，`square(4)` 才是**真的开火**。（PEP 8 提示：给函数起名请用 `def square(x)`；lambda 的主场是下面这种"用完即弃"的场景。）

**问题 2：`sort` 的功能是什么？**

`sort()` 是**列表的排序方法**：**原地**重排元素（不新建列表），返回 `None`。

```python
nums = [3, 1, 2]
nums.sort()               # nums 变成 [1, 2, 3]；返回值是 None！
sorted(nums)              # 返回新列表 [1,2,3]，原列表不动——任何可迭代都能喂给它
```

排序规则：默认按元素本身的 `<` 比较——数字比大小、字符串比字典序、**元组逐位比较**（`(1,2) < (1,3)`：先比第一位，相同再比第二位）。

**问题 3：`intervals.sort(key=lambda item: (item[0], item[1]))` 实现了什么？**

```python
intervals = [(1, 5), (2, 3), (1, 2)]
intervals.sort(key=lambda item: (item[0], item[1]))
# 结果：[(1, 2), (1, 5), (2, 3)]
```

- `intervals` 是"区间列表"，每个元素是 `(起点, 终点)`；
- `key=` 的含义：排序前，**把每个元素变换成一把"用来比较的钥匙"**——排序实际比较的是钥匙，而不是元素本身；
- 这把钥匙是元组 → 按逐位比较：**先按起点升序；起点相同再按终点升序**。这是"合并区间"（LeetCode 56）类题目的标准第一步预处理。

更实用的钥匙形态（负数技巧，01 篇的 `**` 运算的邻居）：

```python
intervals.sort(key=lambda x: (x[0], -x[1]))
# 起点升序、终点降序：起点相同时，"区间更长的"排前面——贪心/区间调度常用
```

（顺带：`(item[0], item[1])` 其实就等于 `item` 本身——上面是教学展开写法；真正的高级用法是变换，如 `key=len`、`key=lambda s: s.lower()`。）

### key 加括号的致命区别

```python
intervals.sort(key=sort_key)     # ✓ 把"函数本身"交给排序，排序会对每个元素调用它
intervals.sort(key=sort_key())   # ✗ 立刻调用函数，把返回值（一个元组？）当 key 传进去
                                  #    key 需要的是"函数"，不是值 → TypeError
```

这就是第一节的伏笔回收：**函数是一等公民——可以像值一样被传递**。`key=sort_key` 传递的是"配方"；`key=sort_key()` 是"现在就做菜，把菜递给排序"。

### 复杂逻辑写成普通函数

```python
def sort_key(item):
    start, end = item
    return start, -end           # 多值返回 = 返回元组（第一节讲过）

intervals.sort(key=sort_key)
```

lambda 只装得下**一个表达式**；解包、分支、多行逻辑请用 `def`——可读性远比短重要。

## 六、递归

递归函数直接或间接调用自己。必须有两要素：

1. **终止条件**：最小的问题直接返回，不再递归（否则无穷调用）；
2. **递归关系**：把当前问题**缩小**成同样形状的子问题。

```python
def factorial(n):
    if n <= 1:                    # 终止条件：最小问题
        return 1
    return n * factorial(n - 1)   # 递归关系：n! = n × (n-1)!
```

执行 `factorial(4)` 时的调用栈（**后进先出**：一层层压进去，到底后再一层层结算回来）：

```text
factorial(4)
  factorial(3)
    factorial(2)
      factorial(1) -> 1     # 触底：终止条件返回
    -> 2                    # 2 * 1
  -> 6                      # 3 * 2
-> 24                       # 4 * 6
```

### 递归处理树（分治思想）

```python
def max_depth(root):
    if root is None:               # 终止：空树深度为 0
        return 0
    left_depth = max_depth(root.left)     # 子问题：左子树的最大深度
    right_depth = max_depth(root.right)   # 子问题：右子树的最大深度
    return max(left_depth, right_depth) + 1   # 合并：左右较大者 + 当前层
```

树是递归的天然主场：**"树的最大深度 = max(左子树深度, 右子树深度) + 1"**——大问题拆成结构完全相同的子问题，`None` 触底。DFS、回溯、分治全是这个骨架。

用 02 篇的话再读一遍递归：**状态** = 每层调用的局部变量 + 调用栈本身；**控制流** = if 判终止、递归调用推进。

### 深度的代价

递归深度过大触发 `RecursionError`（默认上限约 1000 层，`sys.getrecursionlimit()` 可查）。**链表、大图**这类可能很深的结构，优先用**显式栈**（自己维护一个 `stack = []`，循环代替递归——02 篇的 DFS 表格里那行的展开形态）。

## 七、自测（答案在引用块里，先自己写）

**1.** 写 `count_even(nums)` 返回偶数个数。
**2.** 写 `divide(a, b)`，当 `b == 0` 时返回 `None`。
**3.** 写递归函数求列表元素之和。
**4.** 分别用**返回值**和 **nonlocal** 实现二叉树节点计数，比较两种写法的可读性。

> **答案**
>
> ```python
> # 1. 计数（生成器 + sum 一行流；% 判偶性来自 02 篇）
> def count_even(nums):
>     return sum(1 for x in nums if x % 2 == 0)
>
> # 2. 除零返回 None
> def divide(a, b):
>     if b == 0:
>         return None
>     return a / b
>
> # 3. 递归求和：终止 = 空列表返回 0；关系 = 首元素 + 其余的和
> def list_sum(nums):
>     if not nums:
>         return 0
>     return nums[0] + list_sum(nums[1:])
>
> # 4a. 返回值版（推荐）：答案沿返回值向上汇聚，零外部状态
> def count_nodes(root):
>     if root is None:
>         return 0
>     return 1 + count_nodes(root.left) + count_nodes(root.right)
>
> # 4b. nonlocal 版：闭包累加
> def count_nodes_nonlocal(root):
>     count = 0
>     def dfs(node):
>         nonlocal count
>         if node is None:
>             return
>         count += 1
>         dfs(node.left)
>         dfs(node.right)
>     dfs(root)
>     return count
> ```
>
> **可读性对比**：返回值版核心只有一行 `1 + 左 + 右`，与数学定义严丝合缝，不需要维护外部状态；nonlocal 版要额外声明、要小心忘写 `nonlocal` 的 `UnboundLocalError`。结论：**能用返回值优先返回值**（第四节建议的现场证明）。

## 下一篇

候选：容器进阶（浅拷贝/深拷贝、推导式、集合运算）或第一篇正式 LeetCode 题解（把 02 的双指针 + 03 的函数组织成完整题解）。学到哪写哪。

---

*新笔记放 `src/content/blog/`，frontmatter 带 `series: 'Python 基础'`，[专栏页](/series/python-basics/)自动收录。*
