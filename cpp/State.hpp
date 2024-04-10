#ifndef STATE_HPP
#define STATE_HPP

#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <tuple>
#include <memory>
#include "Piece.hpp" // 根据你的项目结构，可能需要调整这个路径

class State {
public:
    std::vector<std::vector<int>> board; // 棋盘或方块的当前状态
    int landingHeight; // 最后一个方块放置时的高度
    int rowsEliminated; // 已消除的行数

    // 构造函数
    explicit State(std::vector<std::vector<int>> board);
    
    // 检查游戏是否结束
    bool isOver();
    
    // 计算行转换
    int rowTransitions();
    
    // 计算列转换
    int colTransitions();
    
    // 根据给定的方块值和方块映射计算下一个状态
    std::vector<std::tuple<int, int, std::unique_ptr<State>>> nextStates(int value, const std::unordered_map<int, Piece>& piece_map);
    
    // 检查并清除已填满的行
    int checkLineClear(std::vector<int> layers);
    
    // 计算当前状态的分数
    int score();
    
    // 计算给定方块值的最佳放置
    std::pair<int, int> best1(int value);

    std::pair<int, int> best1_(int value, int& max_score);
    
    // 计算给定两个方块值的最佳放置
    std::pair<int, int> best2(int val1, int val2);

    std::pair<int, int> best2_(int val1, int val2, int& max_score);

    // 计算最差的下一个方块
    int worstBlock2(int val);
    int worstBlock1();
    int easiestBlock1();
    int easiestBlock2(int val);
};

#endif // STATE_HPP
