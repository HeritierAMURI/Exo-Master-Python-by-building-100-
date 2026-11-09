import time
from turtle import Screen, Turtle
from snake import Snake

# 1. Initialisation de l'écran
screen = Screen()
screen.setup(width=600, height=600)
screen.bgcolor("#F5F5F5")
screen.title("Snake Game")
# Desactive le tracer temporairement pour éviter le flash
screen.tracer(0)

snake = Snake()

screen.listen()
screen.onkey(snake.up, "Up")
screen.onkey(snake.down, "Down")
screen.onkey(snake.left, "Left")
screen.onkey(snake.right, "Right")

game_is_on = True
while game_is_on:
    screen.update()
    time.sleep(0.1)

    snake.move()





# 3. Rafraîchissement unique pour tout afficher d'un coup
screen.update()
# 4. Garde la fenêtre ouverte en continu (DOIT être la toute dernière ligne)
screen.mainloop()
