import random

rock = '''
    _______
---'   ____)
      (_____)
      (_____)
      (____)
---.__(___)
'''

paper = '''
    _______
---'   ____)____
          ______)
          _______)
         _______)
---.__________)
'''

scissors = '''
    _______
---'   ____)____
          ______)
       __________)
      (____)
---.__(___)
'''

game_images = [rock, paper, scissors]














# 2. Comment remplacer le switch...case en Python ?
role = "heritier"
match role:
    case "admin":
        print("Accès total")
    case "user":
        print("Accès limité")
    case _:  # Le tiret du bas (_) remplace le "default" du switch
        print("Accès refusé")