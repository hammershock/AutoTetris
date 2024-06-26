import argparse

import pygame
from tqdm import tqdm

from tetris import PyTris, Mode
from launch_settings import launch_settings_window


class TetrisGUI:
    def __init__(self, game: PyTris, cell_size=30, fps=30, drop_interval=2.0, headless=False):
        self.game = game
        self.cell_size = cell_size
        self.fps = fps
        self.drop_interval = drop_interval  # 下落时间间隔， 0不自动下落，负数立即下落
        self.headless = headless  # 是否开启无头模式，即可以不显示画面
        
        self.colors = [
            (0, 0, 0),
            (81, 130, 137),
            (132, 147, 170),
            (200, 161, 126),
            (220, 222, 175),
            (117, 136, 109),
            (142, 128, 150),
            (144, 79, 85)
        ]
        self.names = {1: 'I', 2: 'J', 3: 'L', 4: 'O', 5: 'S', 6: 'T', 7: 'Z'}
        
        self.clock = pygame.time.Clock()
        if not self.headless:
            pygame.init()
            self.screen = pygame.display.set_mode((game.w * cell_size, game.h * cell_size))
            pygame.display.set_caption('PyTris')
            
            self.font = pygame.font.SysFont("Arial", 24)
    
    def draw_block_with_shadow(self, x, y, color):
        # 绘制小方块本身
        pygame.draw.rect(self.screen, color,
                         pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size),
                         border_radius=max(self.cell_size // 5, 5))  # 使用最小值以确保在小方块尺寸下也能正常显示圆角
        
        # 阴影颜色
        shadow_color_lighter = [max(0, c - 30) for c in color]  # 上、左阴影稍亮
        shadow_color_darker = [max(0, c - 60) for c in color]  # 下、右阴影更暗
        
        # 绘制下边缘和右边缘的阴影
        pygame.draw.line(self.screen, shadow_color_darker,
                         ((x + 1) * self.cell_size - 2, y * self.cell_size),
                         ((x + 1) * self.cell_size - 2, (y + 1) * self.cell_size), 2)  # 右边缘
        pygame.draw.line(self.screen, shadow_color_darker,
                         (x * self.cell_size, (y + 1) * self.cell_size - 2),
                         ((x + 1) * self.cell_size, (y + 1) * self.cell_size - 2), 2)  # 下边缘
        
        # 绘制上边缘和左边缘的阴影
        pygame.draw.line(self.screen, shadow_color_lighter,
                         (x * self.cell_size, y * self.cell_size),
                         ((x + 1) * self.cell_size, y * self.cell_size), 2)  # 上边缘
        pygame.draw.line(self.screen, shadow_color_lighter,
                         (x * self.cell_size, y * self.cell_size),
                         (x * self.cell_size, (y + 1) * self.cell_size), 2)  # 左边缘
    
    def draw_grid(self):
        for y in range(self.game.h):
            for x in range(self.game.w):
                cell_value = self.game.view[y, x]
                if cell_value:  # 仅对非空单元格添加阴影效果
                    color = self.colors[int(cell_value)]
                    self.draw_block_with_shadow(x, y, color)
    
    def draw_text(self, text, position, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)
    
    def run(self):
        running = True
        last_fall_time = pygame.time.get_ticks()
        p_bar = tqdm()
        while running:
            if not self.headless:
                # 显示
                self.screen.fill((0, 0, 0))
                self.draw_grid()
                self.draw_text(f'Score: {self.game.score}', (10, 10))
                self.draw_text(f'Next: {self.names[self.game.next[0]] if self.game.next is not None else "???"}',
                               (10, 30), (255, 255, 0))
                if self.game.game_over:
                    self.draw_text('Game Over', (10, 50), (255, 0, 0))
                
                pygame.display.flip()
                
                # 响应事件
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.game.move_piece(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.game.move_piece(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.game.drop()
                        elif event.key == pygame.K_UP and not self.game.game_over:
                            self.game.rotate_piece()
                        elif self.game.game_over and event.key == pygame.K_SPACE:
                            self.game.start_game()
            
            # 自动下落逻辑
            if self.drop_interval < 0:  # 小于0直接落底
                p_bar.update()
                p_bar.set_postfix(score=self.game.score)
                self.game.drop()
            
            elif (self.drop_interval != 0 and
                  pygame.time.get_ticks() - last_fall_time > self.drop_interval * 1000):  # 2s
                self.game.move_piece(0, 1)
                last_fall_time = pygame.time.get_ticks()
            
            if self.headless:
                if self.game.game_over:
                    p_bar.close()
                    p_bar = tqdm()
                    input('Press any key to restart')
                    self.game.start_game()
            else:
                self.clock.tick(self.fps)  # 稳定以fps循环


def parse_args():
    parser = argparse.ArgumentParser(description="Start Game PyTris")
    parser.add_argument("--width", "-W", type=int, default=10, help="游戏区域的宽度")
    parser.add_argument("--height", "-H", type=int, default=20, help="游戏区域的高度")
    parser.add_argument("--autoplay", action="store_true", help="启用自动决策模式")
    parser.add_argument("--turbo", action="store_true", help="启用加速推理模式")
    parser.add_argument("--mode", type=str, choices=['very-easy', 'easy', 'medium', 'hard', 'extreme'], default="easy",
                        help="游戏难度模式")
    parser.add_argument("--drop-interval", type=float, default=1.0, help="方块下落间隔")
    parser.add_argument("--fps", type=int, default=60, help="帧率")
    parser.add_argument("--headless", action="store_true", help="启用无头模式（不显示GUI）")
    parser.add_argument("--bag7-disabled", action="store_true", help="禁用改进的方块生成算法bag7")
    
    args = parser.parse_args()
    return args


def main():
    settings, success = launch_settings_window()
    if not success:
        return
    
    mode_mapping = {
        'very-easy': Mode.very_easy,
        'easy': Mode.easy,
        'medium': Mode.medium,
        'hard': Mode.hard,
        'extreme': Mode.extreme
    }
    
    game_mode = mode_mapping.get(settings['mode'], Mode.easy)
    
    game = PyTris(w=settings['width'], h=settings['height'], autoplay=settings['autoplay'],
                  turbo=settings['turbo'], mode=game_mode, bag7=settings['bag7'])
    gui = TetrisGUI(game, drop_interval=-1 if settings['instant_drop'] else (0 if settings['disable_auto_drop'] else settings['drop_interval']), fps=settings['fps'], headless=settings['headless'])
    game.start_game()
    gui.run()


if __name__ == '__main__':
    main()
    