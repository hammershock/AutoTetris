#ifndef PIECE_HPP
#define PIECE_HPP

#include <vector>
#include <unordered_map>
#include <utility> // 对于 std::pair

// Piece类的声明
class Piece {
public:
    int value; // 方块的类型值
    int orient; // 方块的旋转方向
    std::vector<std::pair<int, int>> posRels; // 方块的相对位置关系

    // 构造函数声明
    Piece();
    Piece(int init_value, int init_orient, std::vector<std::pair<int, int>> init_posRels);
};

// create_pieces函数声明，用于生成所有方块及其旋转状态的映射
std::unordered_map<int, Piece> create_pieces();

// get_rotated_shape函数声明，用于计算给定形状在特定旋转状态下的新形状
std::vector<std::pair<int, int>> get_rotated_shape(const std::vector<std::pair<int, int>>& shape, int orient);

#endif // PIECE_HPP
