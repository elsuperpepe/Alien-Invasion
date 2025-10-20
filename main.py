from settingss import SettingSs
from gamestats import GameStats
from scoreboard import Scoreboard
from buttom import Buttom
from ship import Ship
from bullet import Bullet
from alien import Alien
import sys
from time import sleep
import pygame

class AlienInvasion: 
    def __init__(self):
        self.settings = SettingSs()
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()    
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        self._update_aliens()
        self.game_active = False
        self.play_buttom = Buttom(self, "Play")
        self.clock = pygame.time.Clock()

        

    def run_game(self):
        #Main game loop    
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen() 
            
            
    def _check_events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit() 

            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pot = pygame.mouse.get_pos()
                self._check_play_buttom(mouse_pot)
    
    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_q:
            sys.exit()

    def _check_play_buttom(self, mouse_pot):
        buttom_clicked = self.play_buttom.rect.collidepoint(mouse_pot)

        if buttom_clicked and not self.game_active:
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.game_active = True
            self.bullets.empty()
            self.aliens.empty()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self._create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)

    
    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
    
    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet) 

        self._check_bullet_alien_collisions() 
    
    
    def _check_bullet_alien_collisions(self):         
            collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)
            
            if collisions:
                for aliens in collisions.values():
                    self.stats.score += self.settings.alien_points * len(aliens)

                self.sb.prep_score()
                self.sb.check_high_score()

            if not self.aliens:
                self.bullets.empty()
                self._create_fleet()
                self.settings.increase_speed()
                self.stats.level += 1
                self.sb.prep_level()
                


    def _update_aliens(self):
        self._check_fleet_edges()   
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            self._check_aliens_bottom()

    
    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites(): 
            if alien.rect.bottom >= self.settings .screen_height:
                self._ship_hit()
                break

    def _ship_hit(self):
        if self.stats.ship_left > 0:
            self.stats.ship_left -= 1
            self.sb.prep_ships()
            self.bullets.empty()
            self.aliens.empty()
            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self.game_active = False

        
        
    def _create_fleet(self):
        alien = Alien(self)

        alien_width, alien_height = alien.rect.size
        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            current_x = alien_width
            current_y += 2 * alien_height
    
    def _create_alien(self, x_position, y_position):

        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *=- 1



    def _update_screen(self):
    
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.drawn_bullet()
        self.ship.blitme()  # Draw the ship 
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.game_active: 
            self.play_buttom.draw_buttom()
        pygame.display.flip()  


if __name__ == "__main__":
    ai = AlienInvasion()
    ai.run_game()