#include"Piece.hpp"
#include"State.hpp"
#include<iostream>


int main(){
    State state = State({{0, 0, 0}, {0, 0, 0}, {0, 0, 0}});
    auto piece_map = create_pieces();
    state.nextStates(3, piece_map);
    return 0;
}
