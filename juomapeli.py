import pygame
import random
import math

pygame.init()

screen = pygame.display.set_mode((1000, 900))
pygame.display.set_caption("Sly Cooper Juomapeli")

clock = pygame.time.Clock()

running = True
started = False
game_over = False
last_scored = None
wheel_result = None
win_screen_started = None
wheel_spin_started = None
win_screen_delay = 1000
wheel_spin_duration = 3000
wheel_final_rotation = 0
bonus_wheel_result = None
bonus_wheel_started = None
bonus_wheel_announcement_duration = 1000
bonus_wheel_spin_duration = 2500
bonus_wheel_duration = bonus_wheel_announcement_duration + bonus_wheel_spin_duration + 500
bonus_wheel_final_rotation = 0

sly_img = pygame.transform.smoothscale(pygame.image.load("sly.jpg").convert(), (130, 130))
bentley_img = pygame.transform.smoothscale(pygame.image.load("bentley.jpg").convert(), (130, 130))
murray_img = pygame.transform.smoothscale(pygame.image.load("murray.png").convert(), (130, 130))
dimitri_img = pygame.transform.smoothscale(pygame.image.load("dimitri.jpg").convert(), (130, 130))

chars = [("Sly", sly_img), ("Bentley", bentley_img), ("Murray", murray_img), ("Dimitri", dimitri_img)]
scores = {"Sly": 0, "Bentley": 0, "Murray": 0, "Dimitri": 0}
name_colors = {
    "Sly": (70, 150, 255),
    "Bentley": (50, 210, 100),
    "Murray": (255, 130, 190),
    "Dimitri": (180, 100, 255),
}
drink_amounts = {}

button_rect = pygame.Rect((screen.get_width() - 360) // 2, 20, 360, 75)
spin_rect = pygame.Rect((screen.get_width() - 260) // 2, 810, 260, 65)
reset_rect = pygame.Rect((screen.get_width() - 260) // 2, 810, 260, 65)
start_y = 560
lane_x = {"Sly": 70, "Bentley": 70, "Murray": 70, "Dimitri": 70}


def draw_centered_parts(parts, font, center):
    rendered = [font.render(text, True, color) for text, color in parts]
    x = center[0] - sum(text.get_width() for text in rendered) // 2
    for text in rendered:
        screen.blit(text, (x, center[1] - text.get_height() // 2))
        x += text.get_width()


def draw_wheel(center, radius, rotation):
    wheel_values = [1, 2, 3, 4, 5]
    wheel_colors = [
        (70, 130, 220),
        (60, 170, 100),
        (220, 100, 150),
        (150, 90, 210),
        (220, 160, 60),
    ]
    label_font = pygame.font.SysFont(None, max(30, round(radius * 0.24)))

    for index, value in enumerate(wheel_values):
        middle_angle = -90 + rotation + index * 72
        start_angle = middle_angle - 36
        points = [center]
        for step in range(13):
            angle = math.radians(start_angle + step * 72 / 12)
            points.append((
                round(center[0] + radius * math.cos(angle)),
                round(center[1] + radius * math.sin(angle)),
            ))
        pygame.draw.polygon(screen, wheel_colors[index], points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 3)

        label_radius = radius * 0.62
        label_angle = math.radians(middle_angle)
        label = label_font.render(f"{value}x", True, (255, 255, 255))
        label_center = (
            round(center[0] + label_radius * math.cos(label_angle)),
            round(center[1] + label_radius * math.sin(label_angle)),
        )
        screen.blit(label, label.get_rect(center=label_center))

    pygame.draw.circle(screen, (255, 255, 255), center, radius, 4)
    pointer_half_width = max(18, round(radius * 0.11))
    pointer_height = max(24, round(radius * 0.14))
    pygame.draw.polygon(
        screen,
        (255, 255, 255),
        [
            (center[0] - pointer_half_width, center[1] - radius - pointer_height),
            (center[0] + pointer_half_width, center[1] - radius - pointer_height),
            (center[0], center[1] - radius + pointer_height // 2),
        ],
    )


while running:
    now = pygame.time.get_ticks()
    if bonus_wheel_started is not None and now - bonus_wheel_started >= bonus_wheel_duration:
        bonus_wheel_started = None
    if game_over and bonus_wheel_started is None and win_screen_started is None:
        win_screen_started = now

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not started:
                if button_rect.collidepoint(event.pos):
                    started = True
            elif bonus_wheel_started is not None:
                pass
            elif game_over:
                now = pygame.time.get_ticks()
                if wheel_spin_started is None:
                    if (
                        win_screen_started is not None
                        and now - win_screen_started >= win_screen_delay
                        and spin_rect.collidepoint(event.pos)
                    ):
                        wheel_result = random.choices(
                            [1, 2, 3, 4, 5],
                            weights=[50, 20, 15, 10, 5],
                            k=1,
                        )[0]
                        wheel_spin_started = now
                        wheel_final_rotation = 360 * 5 + (-(wheel_result - 1) * 72 % 360)
                elif now - wheel_spin_started >= wheel_spin_duration and reset_rect.collidepoint(event.pos):
                    scores = {"Sly": 0, "Bentley": 0, "Murray": 0, "Dimitri": 0}
                    drink_amounts = {}
                    game_over = False
                    last_scored = None
                    wheel_result = None
                    win_screen_started = None
                    wheel_spin_started = None
                    wheel_final_rotation = 0
                    bonus_wheel_result = None
                    bonus_wheel_started = None
                    bonus_wheel_final_rotation = 0
            else:
                if button_rect.collidepoint(event.pos):
                    chosen = random.choice(["Sly", "Bentley", "Murray", "Dimitri"])
                    last_scored = chosen
                    scores[chosen] += 1

                    if random.random() < 0.20:
                        eligible = [name for name, score in scores.items() if score > 0]
                        reduced = random.choice(eligible)
                        scores[reduced] -= 1

                    if random.random() < 0.05:
                        bonus_wheel_result = random.choices(
                            [1, 2, 3, 4, 5],
                            weights=[50, 20, 15, 10, 5],
                            k=1,
                        )[0]
                        bonus_wheel_started = pygame.time.get_ticks()
                        bonus_wheel_final_rotation = (
                            360 * 5 + (-(bonus_wheel_result - 1) * 72 % 360)
                        )

                    if scores[chosen] >= 10:
                        winner = max(scores, key=scores.get)
                        drink_amounts = {name: scores[winner] - scores[name] for name in scores if name != winner}
                        game_over = True
                        win_screen_started = (
                            None if bonus_wheel_started is not None else pygame.time.get_ticks()
                        )

    screen.fill((30, 30, 30))

    if not started:
        pygame.draw.rect(screen, (0, 180, 80), button_rect)
        font = pygame.font.SysFont(None, 48)
        text = font.render("Aloita", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=button_rect.center))
    else:
        gap = 20
        total_width = sum(img.get_width() for _, img in chars) + gap * (len(chars) - 1)
        start_x = (screen.get_width() - total_width) // 2
        bottom_y = screen.get_height() - 200
        level_height = 50

        for name, img in chars:
            y_offset = scores[name] * level_height
            char_x = start_x
            char_y = bottom_y - y_offset - 20

            screen.blit(img, (char_x, char_y))
            if name == last_scored:
                outline_rect = pygame.Rect(char_x - 4, char_y - 4, img.get_width() + 8, img.get_height() + 8)
                pygame.draw.rect(screen, name_colors[name], outline_rect, width=4)
            score_text = pygame.font.SysFont(None, 36).render(str(scores[name]), True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(char_x + img.get_width() // 2, char_y + img.get_height() + 32))
            screen.blit(score_text, score_rect)
            start_x += img.get_width() + gap

        if bonus_wheel_started is not None:
            panel_rect = pygame.Rect(
                (screen.get_width() - 700) // 2,
                (screen.get_height() - 740) // 2,
                700,
                740,
            )

            elapsed = pygame.time.get_ticks() - bonus_wheel_started
            if elapsed < bonus_wheel_announcement_duration:
                if (elapsed // 150) % 2 == 0:
                    title_font = pygame.font.SysFont(None, 80)
                    title = title_font.render("BONUS PYÖRÄ!!!", True, (255, 255, 0))
                    screen.blit(title, title.get_rect(center=panel_rect.center))
            else:
                wheel_elapsed = elapsed - bonus_wheel_announcement_duration
                progress = min(wheel_elapsed / bonus_wheel_spin_duration, 1)
                eased_progress = 1 - (1 - progress) ** 3
                rotation = bonus_wheel_final_rotation * eased_progress
                wheel_center = (screen.get_width() // 2, screen.get_height() // 2)
                draw_wheel(wheel_center, 185, rotation)

                if wheel_elapsed >= bonus_wheel_spin_duration:
                    result_font = pygame.font.SysFont(None, 42)
                    result = result_font.render(f"{bonus_wheel_result}x", True, (255, 255, 0))
                    screen.blit(result, result.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 65)))
        elif game_over:
            if pygame.time.get_ticks() - win_screen_started >= win_screen_delay:
                panel_rect = pygame.Rect(
                    (screen.get_width() - 780) // 2,
                    25,
                    780,
                    screen.get_height() - 50,
                )
                pygame.draw.rect(screen, (0, 0, 0), panel_rect, border_radius=12)

                winner = max(scores, key=scores.get)
                title_font = pygame.font.SysFont(None, 64)
                draw_centered_parts(
                    [(winner, name_colors[winner]), (" on paras!", (255, 255, 0))],
                    title_font,
                    (panel_rect.centerx, panel_rect.y + 65),
                )

                if wheel_spin_started is None:
                    draw_wheel((screen.get_width() // 2, screen.get_height() // 2), 190, 0)
                    pygame.draw.rect(screen, (0, 180, 80), spin_rect, border_radius=8)
                    spin_font = pygame.font.SysFont(None, 42)
                    spin_text = spin_font.render("SPIN", True, (255, 255, 255))
                    screen.blit(spin_text, spin_text.get_rect(center=spin_rect.center))
                else:
                    elapsed = pygame.time.get_ticks() - wheel_spin_started
                    progress = min(elapsed / wheel_spin_duration, 1)
                    eased_progress = 1 - (1 - progress) ** 3
                    rotation = wheel_final_rotation * eased_progress
                    draw_wheel((screen.get_width() // 2, screen.get_height() // 2), 190, rotation)

                    if elapsed >= wheel_spin_duration:
                        result_font = pygame.font.SysFont(None, 42)
                        result_text = result_font.render(f"Kertoimeksi: {wheel_result}x", True, (255, 255, 0))
                        screen.blit(result_text, result_text.get_rect(center=(panel_rect.centerx, 660)))

                        loser_font = pygame.font.SysFont(None, 36)
                        loser_y = 710
                        for name in sorted(drink_amounts):
                            amount = drink_amounts[name] * wheel_result
                            draw_centered_parts(
                                [(name, name_colors[name]), (f" juo {amount}", (255, 255, 255))],
                                loser_font,
                                (panel_rect.centerx, loser_y),
                            )
                            loser_y += 40

                        pygame.draw.rect(screen, (180, 0, 0), reset_rect, border_radius=8)
                        font = pygame.font.SysFont(None, 42)
                        reset_text = font.render("Uudelleen", True, (255, 255, 255))
                        screen.blit(reset_text, reset_text.get_rect(center=reset_rect.center))
        else:
            pygame.draw.rect(screen, (0, 180, 80), button_rect)
            font = pygame.font.SysFont(None, 40)
            text = font.render("Asia selvä siideri", True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=button_rect.center))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

