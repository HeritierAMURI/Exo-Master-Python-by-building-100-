# Subscripting
print("Hello"[0])

# String
print("123" + "345")

# Integer = Whole number
print(123 + 345)

# Large Integers
print(123_456_789)

# Float = Floating Point Number
print(3.14159)

# Boolean
print(True)
print(False)




# --- 1. ZONE DE CRÉATION ---
def ma_fonction():
    """Ceci est le texte de ma documentation secrète !"""
    return "Bonjour"
# Si vous survolez 'ma_fonction' ici, RIEN ne s'affiche.


# --- 2. ZONE D'UTILISATION (Plus bas dans le script) ---

# Rapprochez votre souris et survolez le mot 'ma_fonction' ci-dessous :
texte = ma_fonction() 
#  C'est ICI que la magie opère ! Une bulle va s'ouvrir instantanément 
# avec le message : "Ceci est le texte de ma documentation secrète !"