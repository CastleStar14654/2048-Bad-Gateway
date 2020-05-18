# 2048-Bad-Gateway
Group `502 Bad Gateway`'s stupid 2048 player for SESSDSA, 2020 Spring, PKU.

For more information about the game, c.f. submodule [`sessdsa.2048@pkulab409`](https://github.com/pkulab409/sessdsa.2048)

# 目前策略

1. 进攻为主, 往对方那边推
2. 尽可能好地模拟对方操作 (合并方向方面)

# TODO

参见基本实现了 minimax & alpha-beta 的 [`minimax.py`](./minimax.py). 
1. 更好的获得在对方哪个空位填子的方法 -- 能编程实现的那种  
    [@baikangbo](https://github.com/baikangbo)   
    [@DeweiGong](https://github.com/DeweiGong) : 找一个函数, 算出到对方下子的最好位置
    
    ([@YitingKW](https://github.com/YitingKW) : 比如卡在对方两个可合并棋子之间 -- 如何实现)
2. 估值函数 -- 可以做些实验 (?)  
    考虑棋子之间的关联?  
    [@Kason-pku](https://github.com/Kason-pku) [@YitingKW](https://github.com/YitingKW)
    + 先后手是否可以两个版本
3. 进攻或防守策略的判断. 可以放到 __类变量__ 里.   
    [@CastleStar14654](https://github.com/CastleStar14654)
4. 到时候写报告

# KPI 列表

TODO

## How to clone this repo with its submodule
Open console, checkout to where you intends to save the repo, then
```
git clone --recurse-submodules git@github.com:CastleStar14654/2048-Bad-Gateway.git
```
or
```
git clone git@github.com:CastleStar14654/2048-Bad-Gateway.git
cd 2048-Bad-Gateway
git submodule init
git submodule update
```

# 跑人机
命令行进入 [`sessdsa.2048/src/tools/`](./sessdsa.2048/src/tools/)，运行`python`，
```Python
>>> import round_match
>>> round_match.main(['<玩家1的相对路径>', '<玩家2的相对路径>']) # 机与机
>>> round_match.main([('human.py', -60), '<玩家2的相对路径>'], MAXTIME = 5000) # 人机
```
其他更多参数详见 [`sessdsa.2048/src/tools/round_match.py`](./sessdsa.2048/src/tools/)

# 一些怎么玩的想法

1. 在对面没有足够大之前，不要往对面填——除非为了保护自己
2. 无干涉情况下，经百次实验，随机大概率跑到128(46%)或64(37%)
3. 据hzy说搜两层就能跑过随机AI了
4. 据hzy说开局很难搜，但zyh表示实际上我们可以直接事先遍历开局可能情形存着吧
5. 似乎py版本的棋盘复制棋盘消耗很大
6. zyh's idea: 棋盘割成多个小块，每个小块进行决策，最后各个小块结果加权
7. 主动进攻策略1：把一个大数(64及以上)深入到对方后排(第二行往后)，然后在附近看情况往对方放2利用大数阻碍对方消去最后把对方击垮。
8. 深度搜索+剪枝。格局评价：越单调越好（最大数放在角落）；越平滑越好（都是一样的数）；空格越多越好；空格越聚集越好；加权比较格局，并根据现有格局改变权数？
9. 整理自https://stackoverflow.com/a/22498940/1204143
  1）空格越多越好 2）大数靠边 3）行列内单调（主要看大数）4)相邻且相同的数越多越好（可合并数量多）5)*采用CMA-ES算法？
  最终效果：2048: 100% 4096: 100% 8192: 100% 16384: 94% 32768: 36%
