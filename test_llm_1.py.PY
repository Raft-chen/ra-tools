import pygame
import random

# --- 1. 基础设置 ---
WIDTH = 480
HEIGHT = 600
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED_EMPIRE = (220, 20, 60)    # 帝国 (红色)
BLUE_REBELS = (30, 144, 255)  # 起义军 (蓝色)
GREEN_PLAYER = (0, 255, 127)  # 玩家 (绿色)
YELLOW_BULLET = (255, 215, 0) # 子弹 (金色)

# 初始化 Pygame
pygame.init()
pygame.mixer.init()  # 初始化音效（预留）
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("苍穹权谋：铁翼外交 - 原型版")
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial')

# --- 2. 政治系统核心 ---
# 这是一个全局字典，用来存储你和各方的关系
politics = {
    "Empire": 0,    # 帝国好感度
    "Rebels": 0,    # 起义军好感度
    "Score": 0      # 综合得分
}

def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# --- 3. 游戏角色类 ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 这里用简单的绿色方块代表玩家，以后可以换成飞机图片
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN_PLAYER)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0

    def update(self):
        # 键盘控制移动
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_UP]:
            self.speedy = -8
        if keystate[pygame.K_DOWN]:
            self.speedy = 8
            
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # 边界限制，不让飞机飞出屏幕
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

    def shoot(self):
        # 创建子弹并发射
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 随机决定这个敌人是哪个阵营的
        self.faction = random.choice(["Empire", "Rebels"])
        
        self.image = pygame.Surface((30, 30))
        
        # 根据阵营涂上不同颜色
        if self.faction == "Empire":
            self.image.fill(RED_EMPIRE)
        else:
            self.image.fill(BLUE_REBELS)
            
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(2, 6)
        self.speedx = random.randrange(-1, 2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # 如果飞出屏幕下方，这就意味着你放过了它（这也可能是一种政治选择）
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 6)
            # 重新生成时可能改变阵营（简化逻辑）
            self.faction = random.choice(["Empire", "Rebels"])
            if self.faction == "Empire":
                self.image.fill(RED_EMPIRE)
            else:
                self.image.fill(BLUE_REBELS)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(YELLOW_BULLET)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # 子弹飞出屏幕上方后消失，节省内存
        if self.rect.bottom < 0:
            self.kill()

# --- 4. 游戏主循环 ---

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# 初始生成8个敌人
for i in range(8):
    m = Enemy()
    all_sprites.add(m)
    mobs.add(m)

running = True
game_over = False

while running:
    # 保持帧率
    clock.tick(FPS)

    # A. 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # B. 更新所有物体位置
    all_sprites.update()

    # C. 碰撞检测：子弹击中敌人
    # groupcollide(组1, 组2, 删除组1成员?, 删除组2成员?)
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    
    for hit in hits:
        # hit 是被击中的那个敌人对象
        # 这里是政治玩法的核心逻辑！
        if hit.faction == "Empire":
            politics["Empire"] -= 10  # 得罪帝国
            politics["Rebels"] += 5   # 讨好起义军
            draw_text(screen, "Empire hit!", 18, hit.rect.centerx, hit.rect.top, RED_EMPIRE)
        elif hit.faction == "Rebels":
            politics["Rebels"] -= 10  # 得罪起义军
            politics["Empire"] += 5   # 讨好帝国
            draw_text(screen, "Rebel hit!", 18, hit.rect.centerx, hit.rect.top, BLUE_REBELS)
        
        politics["Score"] += 100
        
        # 销毁一个敌人后，立刻生成一个新的，保持战场繁忙
        m = Enemy()
        all_sprites.add(m)
        mobs.add(m)

    # D. 碰撞检测：敌人撞到玩家 (游戏结束判定)
    hits = pygame.sprite.spritecollide(player, mobs, False)
    if hits:
        running = False # 简单处理：撞到就退出循环

    # E. 画面绘制
    screen.fill(BLACK) # 背景色
    all_sprites.draw(screen)

    # 绘制UI界面（政治仪表盘）
    draw_text(screen, f"Empire Relations: {politics['Empire']}", 18, WIDTH / 4, 10, RED_EMPIRE)
    draw_text(screen, f"Rebel Relations: {politics['Rebels']}", 18, WIDTH * 3 / 4, 10, BLUE_REBELS)
    draw_text(screen, f"Total Score: {politics['Score']}", 18, WIDTH / 2, 40, WHITE)

    # 翻转屏幕（显示绘制内容）
    pygame.display.flip()

pygame.quit()
