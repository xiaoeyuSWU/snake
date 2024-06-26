import pygame
import random
import math

# 初始化 pygame
pygame.init()

# 设置常量
WIDTH, HEIGHT = 640, 480        
CELL_SIZE = 20
V= 6
NUM_MINES = 10  # 地雷数量
hearts = 3  # 初始化生命值为3颗心
bonus_food_eaten = 0

frame_count = 0

# 颜色
WHITE = (255, 255, 255)
GREEN = (0, 155, 0)
DARK_GREEN = (0, 100, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
GRAY = (100, 100, 100)  # 地雷的颜色

# 设置界面颜色
BG_COLOR = WHITE  # 背景颜色

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("贪吃蛇")

# 加载背景图像并将其缩放到屏幕大小
background_image = pygame.image.load('background.jpg')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

clock = pygame.time.Clock()

# 加载字体
font = pygame.font.SysFont('simsun', 25)

def snake_collides_with_bonus_food(snake_head, bonus_food):
    return snake_head == bonus_food

def get_random_position():
    # 食物不会出现在边缘3个格内
    x_min = 3
    y_min = 3
    x_max = (WIDTH // CELL_SIZE) - 3
    y_max = (HEIGHT // CELL_SIZE) - 3
    return (random.randint(x_min, x_max), random.randint(y_min, y_max))

class Snake:
    def __init__(self):
        self.body = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)

    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body = [new_head] + self.body[:-1]

    def grow(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body = [new_head] + self.body

    def collides_with_itself(self):
        return self.body[0] in self.body[1:]

    def collides_with_bounds(self):
        head = self.body[0]
        return head[0] < 0 or head[0] > (WIDTH // CELL_SIZE) - 1 or head[1] < 0 or head[1] > (HEIGHT // CELL_SIZE) - 1

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.color = color
        self.lifetime = random.randint(50, 150)
        self.vel_x = random.uniform(-1, 1)
        self.vel_y = random.uniform(-1, 1)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.size = max(1, self.size - 0.1)  # 粒子逐渐变小
        self.lifetime -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

def create_particles(x, y, color):
    particles = []
    for _ in range(20):  # 生成20个粒子
        particles.append(Particle(x, y, color))
    return particles


def draw_grid():
    grid_color = (230, 230, 230)  # A light grey color
    for x in range(0, WIDTH, CELL_SIZE):  # 绘制垂直线
        pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):  # 绘制水平线
        pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))

def draw_countdown(last_food_time):
    if last_food_time is not None:
        current_time = pygame.time.get_ticks()
        time_left = max(0, 5 - (current_time - last_food_time) // 1000)
        if time_left > 0:
            countdown_text = font.render(f'倒计时: {time_left} 秒', True, GOLD)
            countdown_rect = countdown_text.get_rect()
            countdown_rect.midtop = (WIDTH // 2, 10)
            screen.blit(countdown_text, countdown_rect)
        else:
            last_food_time = None  # 重置倒计时
    return last_food_time



def draw_score(score):
    # 设置得分板文字
    text = font.render(f'你的得分: {score}', True, GOLD)  # 使用金色字体
    # 获得文字的矩形大小
    text_rect = text.get_rect()
    # 设置文字的位置
    text_rect.topleft = (10, 10)
    # 在屏幕上绘制文字
    screen.blit(text, text_rect)

def draw_heart(screen, position, size, color):
    x, y = position
    radius = size // 4
    
    # 绘制左半边的心形
    pygame.draw.circle(screen, color, (x + radius, y + radius), radius)
    pygame.draw.circle(screen, color, (x + 3 * radius, y + radius), radius)
    
    # 绘制下半边的心形
    pygame.draw.polygon(screen, color, [(x, y + radius), 
                                        (x + 2 * radius, y + 4 * radius),
                                        (x + 4 * radius, y + radius),
                                        (x + 2 * radius, y)])


def draw_hearts(hearts):
    heart_size = CELL_SIZE
    for i in range(hearts):
        heart_x = WIDTH - (i + 1) * (heart_size + 10)
        heart_y = 10
        draw_heart(screen, (heart_x, heart_y), heart_size, RED)


# Generate a list of colors forming a gradient between `start_color` and `end_color`.
def get_color_gradient(start_color, end_color, num_segments):
    gradient = []
    for i in range(num_segments):
        factor = i / float(num_segments)
        new_color = tuple([int(start_color[j] + (end_color[j] - start_color[j]) * factor) for j in range(3)])
        gradient.append(new_color)
    return gradient

def draw_snake(snake, frame_count):
    body_gradient = get_color_gradient(GREEN, DARK_GREEN, len(snake.body))

    for idx, segment in enumerate(snake.body):
        segment_color = body_gradient[idx]
        
        if idx == 0:  # 蛇头没有扭动效果
            pygame.draw.rect(screen, segment_color, (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            # Eyes
            eye_x = segment[0] * CELL_SIZE + 5
            eye_y = segment[1] * CELL_SIZE + 5
            pygame.draw.circle(screen, BLACK, (eye_x, eye_y), CELL_SIZE // 10)
            pygame.draw.circle(screen, BLACK, (eye_x + 10, eye_y), CELL_SIZE // 10)
        else:
            # 绘制蛇身的其余部分，移除了扭动效果
            pygame.draw.rect(screen, segment_color, (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_mine(screen, position, size):
    x, y = position
    # 画地雷的主体
    pygame.draw.circle(screen, GRAY, (x + size // 2, y + size // 2), size // 2)
    # 画雷管
    fuse_rect = pygame.Rect(x + size // 4, y - size // 4, size // 2, size // 4)
    pygame.draw.rect(screen, RED, fuse_rect)

def draw_mines(mines):
    for mine in mines:
        mine_position = (mine[0] * CELL_SIZE, mine[1] * CELL_SIZE)
        draw_mine(screen, mine_position, CELL_SIZE)


def draw_food(food):
    # 绘制苹果的主体为红色圆形
    pygame.draw.circle(screen, RED, (food[0] * CELL_SIZE + CELL_SIZE // 2, food[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)
    # 绘制苹果的叶子为绿色较大矩形
    leaf_width = CELL_SIZE // 2
    leaf_height = CELL_SIZE // 4
    leaf_x = food[0] * CELL_SIZE + (CELL_SIZE - leaf_width) // 2
    leaf_y = food[1] * CELL_SIZE - leaf_height // 2  # 将叶子的一部分绘制在苹果的圆形之上
    pygame.draw.rect(screen, GREEN, (leaf_x, leaf_y, leaf_width, leaf_height))

def draw_bonus_food(bonus_food, bonus_food_visible):
    if bonus_food_visible:
        # 桃子的主体
        peach_body_color = (255, 218, 185)  # 桃色
        peach_outer_color = (255, 160, 122)  # 淡红色
        peach_center = (bonus_food[0] * CELL_SIZE + CELL_SIZE // 2, bonus_food[1] * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.circle(screen, peach_outer_color, peach_center, CELL_SIZE // 2)
        pygame.draw.circle(screen, peach_body_color, peach_center, CELL_SIZE // 2 - 2)

        # 桃子的小凹陷
        dip_color = (255, 69, 0)  # 暗红色
        dip_rect = (bonus_food[0] * CELL_SIZE + CELL_SIZE // 2 - 2, bonus_food[1] * CELL_SIZE, 4, CELL_SIZE // 4)
        pygame.draw.ellipse(screen, dip_color, dip_rect)

        # 桃子的叶子
        leaf_color = GREEN
        leaf_rect = (bonus_food[0] * CELL_SIZE + CELL_SIZE // 4, bonus_food[1] * CELL_SIZE, CELL_SIZE // 2, CELL_SIZE // 4)
        pygame.draw.ellipse(screen, leaf_color, leaf_rect)

snake = Snake()
food = get_random_position()
bonus_food = None
bonus_food_visible = False
bonus_food_timer = 0
bonus_food_start_time = None

mines = [get_random_position() for _ in range(NUM_MINES)]  # 地雷位置列表
mine_update_time = pygame.time.get_ticks()  # 地雷更新计时器

score = 0  # 初始化分数
last_food_time = None  # 上次吃到食物的时间
mine_update_time = pygame.time.get_ticks()

running = True
game_start_time = pygame.time.get_ticks()  # 游戏开始时间
particles = []

while running:
    frame_count += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != (0, 1):
                snake.direction = (0, -1)
            elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                snake.direction = (0, 1)
            elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                snake.direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                snake.direction = (1, 0)

    # Check for collisions with bounds or self and reduce hearts instead of ending game
    if snake.collides_with_bounds() or snake.collides_with_itself():
        hearts -= 1
        if hearts == 0:
            running = False
        else:
            # Move the snake back to starting position without changing the length
            snake.body.insert(0, snake.body[0])  # Temporary new head to maintain length
            snake.move()  # Move will remove the last segment, thus keeping the length same
            snake.body[0] = (5, 5)  # Reset head to starting position
            snake.direction = (1, 0)  # Reset direction

    # Check for collision with mines and reduce hearts instead of ending game
    if snake.body[0] in mines:
        particles.extend(create_particles(snake.body[0][0] * CELL_SIZE + CELL_SIZE // 2, snake.body[0][1] * CELL_SIZE + CELL_SIZE // 2, GRAY))
        hearts -= 1
        if hearts == 0:
            running = False
        else:
            mines.remove(snake.body[0])  # Remove the mine that was hit
            # Move the snake back to starting position without changing the length
            snake.body.insert(0, snake.body[0])  # Temporary new head to maintain length
            snake.move()  # Move will remove the last segment, thus keeping the length same
            snake.body[0] = (5, 5)  # Reset head to starting position
            snake.direction = (1, 0)  # Reset direction

    snake.move()

    # 地雷位置更新逻辑
    current_time = pygame.time.get_ticks()
    if current_time - mine_update_time >= 10000:  # 检查是否已经过了10秒
        mines = [get_random_position() for _ in range(NUM_MINES)]  # 更新地雷位置
        mine_update_time = current_time  # 重置地雷更新计时器


    # Check for collision with regular food
    if snake.body[0] == food:
        current_time = pygame.time.get_ticks()
        # 检查是否在5秒内吃到了另一个食物
        if last_food_time and current_time - last_food_time <= 5000:
            score += 2  # 如果是，加2分
        else:
            score += 1  # 否则，加1分
        last_food_time = current_time  # 更新上次吃食物的时间
        particles.extend(create_particles(food[0] * CELL_SIZE + CELL_SIZE // 2, food[1] * CELL_SIZE + CELL_SIZE // 2, RED))
        snake.grow()
        food = get_random_position()


    # Update bonus food state
    current_time = pygame.time.get_ticks()
    seconds_since_start = (current_time - game_start_time) // 1000
    if seconds_since_start % 10 == 0 and bonus_food is None:
        bonus_food = get_random_position()
        bonus_food_visible = True
        bonus_food_start_time = current_time
    elif bonus_food is not None and current_time - bonus_food_start_time >= 5000:
        bonus_food = None
        bonus_food_visible = False

    # Check for collision with bonus food
    if bonus_food and snake_collides_with_bonus_food(snake.body[0], bonus_food):
        score += 5
        snake.grow()
        bonus_food = None
        bonus_food_eaten += 1
        if bonus_food_eaten % 3 == 0:  # Every 3 bonus foods eaten, increase hearts by 1
            hearts += 1

    # Update bonus food visibility
    if bonus_food:
        bonus_food_visible = (current_time // 500) % 2 == 0

    # Render game elements
    screen.blit(background_image, (0, 0))
    # 在每帧的开始
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.lifetime <= 0:
            particles.remove(particle)


    draw_grid()
    draw_snake(snake, frame_count)
    draw_food(food)
    draw_mines(mines)
    if bonus_food and bonus_food_visible:
        draw_bonus_food(bonus_food, bonus_food_visible)
    draw_score(score)
    draw_hearts(hearts)

    # 绘制倒计时
    last_food_time = draw_countdown(last_food_time)

    # Update the screen
    pygame.display.flip()
    clock.tick(V)

# Game over logic
last_food_time = None  # 重置上次吃到食物的时间
screen.fill(BG_COLOR)
final_text = font.render(f'游戏结束~ 你的分数是 {score} 分:)', True, BLACK)
text_rect = final_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
screen.blit(final_text, text_rect)
pygame.display.flip()
pygame.time.wait(3000)

pygame.quit()

