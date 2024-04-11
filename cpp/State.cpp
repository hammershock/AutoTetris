#include<iostream>
#include<vector>
#include<unordered_map>
#include<unordered_set>
#include<tuple>
#include<queue>
#include<algorithm>
#include<cmath>
#include<memory>
#include"Piece.hpp"
#include"State.hpp"
#include<iostream>

using namespace std;

State::State(std::vector<std::vector<int>> board) : board(board), rowsEliminated(0), landingHeight(0) {
    // 确保有具体实现
}

bool State::isOver(){
    // 检验第零行有没有非零元素
    vector<int> first_row = this->board[0];
    for (const int state: first_row){
        if (state > 0) return true;
    }
    return false;
}

int State::rowTransitions(){
    int cnt = 0;
    for (const vector<int> row : this->board){
        int old = 1;
        for (const int item : row){
            if ((item != 0 && old == 0) || (item == 0 && old != 0)){
                cnt++;
                old = item;
            }
        }
        if (old == 0)cnt++;
    }
    return -32 * cnt;
}


int State::colTransitions(){
    int cnt = 0;
    int holes = 0;
    int well_sum = 0;
    for (int j = 0; j < this->board[0].size(); ++j){
        int old = 1;
        bool flag = false;
        int well_cnt = 0;
        for (int i = 0; i < this->board.size(); ++i){
            int left = j-1>=0 ? this->board[i][j-1] : 1;
            int item = this->board[i][j];
            int right = j+1 < this->board[0].size()? this->board[i][j+1] : 1;
            if ((item != 0 && old == 0) || (item == 0 && old != 0)){
                cnt++;
                old = item;
            }
            if (item > 0){
                flag = true;
            }
            if (flag && item == 0){
                holes++;
                flag = false;
            }
            if (left > 0 && right > 0 && item == 0){
                well_cnt += 1;
            } else {
                well_sum += well_cnt * (well_cnt + 1) / 2;
                well_cnt = 0;
            }
        }
        if (old == 0)cnt++;
    }
    return -93 * cnt - 79 * holes - 34 * well_sum;
}


vector<tuple<int, int, unique_ptr<State>>> State::nextStates(int value, const std::unordered_map<int, Piece>& piece_map){
vector<tuple<int, int, unique_ptr<State>>> ret;

// 一般来说有4中旋转方式，对于中心对称的图形有2种， 而对于2×2的O形只有1种
int orient_end = (value == 2 || value == 3 || value == 6) ? 4 : (value == 4 ? 1 : 2);

// 遍历所有可能朝向
for (int orient = 0; orient < orient_end; orient++){
    const Piece& piece = piece_map.at(value * 4 + orient);
    int x_min = board[0].size(), y_min = board.size();
    int x_max = 0, y_max = 0;
    for (auto &[dx, dy] : piece.posRels){
        if (dx > x_max)x_max = dx;
        if (dx < x_min)x_min = dx;
        if (dy > y_max)y_max = dy;
        if (dy < y_min)y_min = dy;
    }

    // 遍历所有可能的下落位置
    for (int x0 = -x_min; x0 < board[0].size() - x_max; x0++){
        int land_y = -1;

        // 寻找下落点
        for (int y0 = -y_min; y0 < board.size() - 1; y0++){
            const Piece& piece = piece_map.at(value * 4 + orient);
            for (auto& [dx, dy]: piece.posRels){
                int x = x0 + dx, y = y0 + dy;
                int next_y = y + 1;

                if (next_y >= board.size() || board[next_y][x] > 0){ // one block land
                    land_y = y0;
                    break;
                } 
            }

            if (land_y > 0){
                break;
                }
        }

        if (land_y < 0) continue;  // another try

        vector<int> layers;
        vector<vector<int>> nextState = board;

        for (auto& [dx, dy]: piece.posRels){
            int x = x0 + dx, y = land_y + dy;
            if (y >= 0 && y < board.size()){
                nextState[y][x] = piece.value;
                layers.push_back(y);
                }
        }

        unique_ptr<State> state = make_unique<State>(nextState);
        state->landingHeight = board.size() - land_y;
        state->checkLineClear(layers);
        ret.emplace_back(std::make_tuple(orient, x0, std::move(state)));
    }
}
return ret;
}



int State::checkLineClear(vector<int> layers){
vector<vector<int>> newGrid = board;
int linesCleared = 0;
unordered_set<int> clearedRows;

for (int i = board.size() - 1; i >= 0; i--){
    vector<int> row = board[i];
    bool cleared = true;
    for (const int item : row){
        if (item == 0){cleared = false; break;}
    }
    if (cleared){
        linesCleared++;
        clearedRows.insert(i);
    } else {
        newGrid[i + linesCleared] = row;
    }
}

for (int i = 0; i < linesCleared; i++) {
    std::fill(newGrid[i].begin(), newGrid[i].end(), 0);
}

int cnt = 0;
for (const int layer: layers){
    if (clearedRows.find(layer) != clearedRows.end())cnt++;
}
board = newGrid;
this->rowsEliminated = 34 * linesCleared * cnt;
return this->rowsEliminated;
}

int State::score(){
    int score = -45 * this->landingHeight + this->rowsEliminated + this->rowTransitions() + this->colTransitions();
    return score;
}


pair<int, int> State::best1(int value){
    int max_score = INT16_MIN;
    return best1_(value, max_score);
}

std::pair<int, int> State::best1_(int value, int& max_score){
    std::unordered_map<int, Piece> piece_map = create_pieces();
    auto ret = this->nextStates(value, piece_map);
    int max_orient = -1, max_x0 = -1;
    for (auto &[orient, x0, state]: ret){
        int score = state->score();
            if (score > max_score){
                max_score = score;
                max_orient = orient;
                max_x0 = x0;
            }
        }
return make_pair(max_orient, max_x0);
}

std::pair<int, int> State::best2(int val1, int val2){
    int max_score = INT32_MIN;
    return best2_(val1, val2, max_score);
}

std::pair<int, int> State::best2_(int val1, int val2, int& max_score){
    std::unordered_map<int, Piece> piece_map = create_pieces();
    int max_orient = -1, max_x0 = -1;

    auto ret = this->nextStates(val1, piece_map);
    for (auto &[orient, x0, state]: ret){
        auto ret2 = state->nextStates(val2, piece_map);
        
        for (auto &[orient2, x02, state2]: ret2){
            int score = state2->score() + state->score();
            if (score > max_score){
                max_score = score;
                max_orient = orient;
                max_x0 = x0;
            }
        }
    }
    return make_pair(max_orient, max_x0);
}

std::vector<std::pair<int, int>> State::scores2(int val) {
    std::vector<std::pair<int, int>> scores; // 存储val2和对应的score
    for (int val2 = 1; val2 < 8; val2++) {
        int score = INT32_MIN;
        auto [orient, x0] = this->best2_(val, val2, score);
        scores.emplace_back(val2, score); // 存储val2和它的score
    }
    std::sort(scores.begin(), scores.end(), [](const std::pair<int, int>& a, const std::pair<int, int>& b) {
            return a.second < b.second; // 使用score作为排序依据
        });
    return scores;
    }

std::vector<std::pair<int, int>> State::scores1(){
    std::vector<std::pair<int, int>> scores; // 存储val2和对应的score
    for (int val = 1; val < 8; val++){
        int score = INT32_MIN;
        auto [orient, x0] = this->best1_(val, score);
        scores.emplace_back(val, score); // 存储val2和它的score
    }
    std::sort(scores.begin(), scores.end(), [](const std::pair<int, int>& a, const std::pair<int, int>& b) {
            return a.second < b.second; // 使用score作为排序依据
        });
    return scores;
}
