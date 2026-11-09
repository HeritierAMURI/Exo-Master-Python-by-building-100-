student_scores = [150, 142, 185, 120, 171, 184, 149, 24, 59, 68, 199, 78, 65, 89, 86, 55, 91, 64, 89]

max_score = 0
for score in student_scores:
    if score > max_score:
        max_score = score

print(max_score)























random.seed(42)
print(random.randint(1, 10)) # Affichera TOUJOURS la même valeur à chaque fois que vous lancerez le script.
