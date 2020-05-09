# 2048-Bad-Gateway
Group `502 Bad Gateway`'s stupid 2048 player for SESSDSA, 2020 Spring, PKU.

For more information about the game, c.f. submodule [`sessdsa.2048@pkulab409`](https://github.com/pkulab409/sessdsa.2048)

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

# 一些怎么玩的想法

1. 在对面没有足够大之前，不要往对面填——除非为了保护自己
2. 据说随机只能跑到64——除非你送人头
3. 据hzy说搜两层就能跑过随机AI了
4. 据hzy说开局很难搜，但zyh表示实际上我们可以直接事先遍历开局可能情形存着吧
5. 似乎py版本的棋盘复制棋盘消耗很大
6. zyh's idea: 棋盘割成多个小块，每个小块进行决策，最后各个小块结果加权
