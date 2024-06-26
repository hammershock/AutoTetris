# 自动求解的俄罗斯方块AutoTetris

![效果展示](https://github.com/hammershock/AutoTetris/assets/109429530/3e32731e-a62c-4a58-a374-616f5a6f8d2a)


- 使用Pierre Dellacherie评估算法
- 可供选择的bag7生成函数
- 提供了基于C++的模块扩展，大幅提升推理速度，使用前需要运行`build.sh`进行编译

- 空格键重新开始游戏

## 可选参数：
- `width` 棋盘宽度
- `height` 棋盘高度
- `autoplay`是否开启自动决策
- `turbo`是否开启加速推理（需要编译, build.sh）。
  **⚠️ 注意！** 目前除了medium的所有模式都需要在turbo模式下运行
- `mode` 难度等级：easy, medium, hard, extreme；
  - very-easy: 当前方块以概率1-p出现最有利于玩家的那一个
  - easy:  下一个方块以概率1-p出现最有利于玩家的那一个
  - medium: 下一个方块完全随机出现
  - hard: 下一个方块以概率p出现最不利于玩家的那一个
  - extreme: 禁用下一个方块提示，且当前方块以概率p出现最不利于玩家的那一个
- `drop-interval` 方块下落时间间隔，置0不自动下落，负值立即下落
- `fps` 游戏GUI刷新帧率
- `headless` 开启无头模式，即不显示GUI，以最大速率运行
- `bag7-disabled` 禁用bag7生成算法，改用纯随机生成。默认使用bag7算法生成方块，避免纯随机导致的极端结果，有利于提升游戏公平性


```bash
 python gui.py
```


[参考资料](https://blog.csdn.net/Originum/article/details/81570042 "俄罗斯方块人工智能 [AI]")

