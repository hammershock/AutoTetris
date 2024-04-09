
#include "Piece.hpp"


using namespace std;


Piece::Piece(int init_value, int init_orient, std::vector<std::pair<int, int>> init_posRels)
    : value(init_value), orient(init_orient), posRels(std::move(init_posRels)) {}

Piece::Piece() : value(0), orient(0), posRels() {}

std::vector<std::pair<int, int>> get_rotated_shape(const std::vector<std::pair<int, int>>& shape, int orient);

unordered_map<int, Piece> create_pieces() {
    unordered_map<int, Piece> types;
    vector<vector<pair<int, int>>> shapes = {
        {{0, -1}, {0, 0}, {0, 1}, {0, 2}}, // I
        {{0, -1}, {0, 0}, {0, 1}, {-1, 1}}, // J
        {{0, -1}, {0, 0}, {0, 1}, {1, 1}}, // L
        {{0, 0}, {0, 1}, {1, 0}, {1, 1}}, // O
        {{1, 0}, {0, 0}, {0, 1}, {-1, 1}}, // S
        {{-1, 0}, {0, 0}, {1, 0}, {0, 1}}, // T
        {{-1, 0}, {0, 0}, {0, 1}, {1, 1}}  // Z
    };
    int values[] = {1, 2, 3, 4, 5, 6, 7};

    for (int i = 0; i < shapes.size(); ++i) {
        for (int orient = 0; orient < 4; orient++) {
            std::vector<std::pair<int, int>> posRels = get_rotated_shape(shapes[i], orient);
            int key = values[i] * 4 + orient;
            types[key] = Piece(values[i], orient, posRels);
        }
    }
    return types;
}


vector<pair<int, int>> get_rotated_shape(const vector<pair<int, int>>& shape, int orient) {
    vector<pair<int, int>> result;
    for (const auto& [x, y] : shape) {
        int newX = x, newY = y;
        switch (orient) {
            case 1: // 90度旋转
                newX = y; newY = -x;
                break;
            case 2: // 180度旋转
                newX = -x; newY = -y;
                break;
            case 3: // 270度旋转
                newX = -y; newY = x;
                break;
        }
        result.push_back({newX, newY});
    }
    return result;
}
