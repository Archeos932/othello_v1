import pygame
import sys
import time

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre
TAILLE_FENETRE = 800
TAILLE_CASE = TAILLE_FENETRE // 8
LARGEUR_BARRE_LATERALE = 500
COULEUR_PLATEAU = (34, 139, 34)  # Vert
COULEUR_LIGNE = (0, 0, 0)  # Noir

# Couleurs des pions
COULEUR_NOIR = (0, 0, 0)
COULEUR_BLANC = (255, 255, 255)
COULEUR_BARRE_LATERALE = (200, 200, 200)
COULEUR_TEXTE = (0, 0, 0)

# Initialisation de l'écran
ecran = pygame.display.set_mode((TAILLE_FENETRE + LARGEUR_BARRE_LATERALE, TAILLE_FENETRE))
pygame.display.set_caption("Le jeu de Othello - IA avancée")

# Tableau de pondération pour les mouvements stratégiques
PONDERATION = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10, -2, 5, 1, 1, 5, -2, 10],
    [5, -2, 1, 0, 0, 1, -2, 5],
    [5, -2, 1, 0, 0, 1, -2, 5],
    [10, -2, 5, 1, 1, 5, -2, 10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10, 5, 5, 10, -20, 100]
]

# Initialisation du plateau
def init_plateau():
    tableau = [["_" for _ in range(8)] for _ in range(8)]
    tableau[3][3], tableau[4][4] = "B", "B"
    tableau[3][4], tableau[4][3] = "N", "N"
    return tableau

# Dessine le plateau et la barre latérale
def dessiner_plateau(tableau):
    ecran.fill(COULEUR_PLATEAU)

    # Dessiner les lignes
    for i in range(1, 8):
        pygame.draw.line(ecran, COULEUR_LIGNE, (i * TAILLE_CASE, 0), (i * TAILLE_CASE, TAILLE_FENETRE), 2)
        pygame.draw.line(ecran, COULEUR_LIGNE, (0, i * TAILLE_CASE), (TAILLE_FENETRE, i * TAILLE_CASE), 2)

    # Dessiner les pions
    for ligne in range(8):
        for colonne in range(8):
            if tableau[ligne][colonne] == "N":
                pygame.draw.circle(
                    ecran,
                    COULEUR_NOIR,
                    (colonne * TAILLE_CASE + TAILLE_CASE // 2, ligne * TAILLE_CASE + TAILLE_CASE // 2),
                    TAILLE_CASE // 3,
                )
            elif tableau[ligne][colonne] == "B":
                pygame.draw.circle(
                    ecran,
                    COULEUR_BLANC,
                    (colonne * TAILLE_CASE + TAILLE_CASE // 2, ligne * TAILLE_CASE + TAILLE_CASE // 2),
                    TAILLE_CASE // 3,
                )

    # Dessiner la barre latérale
    pygame.draw.rect(ecran, COULEUR_BARRE_LATERALE, (TAILLE_FENETRE, 0, LARGEUR_BARRE_LATERALE, TAILLE_FENETRE))
    blancs = sum(ligne.count("B") for ligne in tableau)
    noirs = sum(ligne.count("N") for ligne in tableau)
    total = blancs + noirs

    if total > 0:
        proportion_blancs = blancs / total
        proportion_noirs = noirs / total
        pygame.draw.rect(ecran, COULEUR_BLANC, (TAILLE_FENETRE + 20, 20, 160, int(460 * proportion_blancs)))
        pygame.draw.rect(ecran, COULEUR_NOIR, (TAILLE_FENETRE + 20, 20 + int(460 * proportion_blancs), 160, int(460 * proportion_noirs)))

    font = pygame.font.SysFont(None, 24)
    texte_blancs = font.render(f"Blancs: {blancs}", True, COULEUR_TEXTE)
    texte_noirs = font.render(f"Noirs: {noirs}", True, COULEUR_TEXTE)
    ecran.blit(texte_blancs, (TAILLE_FENETRE + 20, 500))
    ecran.blit(texte_noirs, (TAILLE_FENETRE + 20, 530))

# Vérifie si un mouvement est valide
def move_verif(tableau, ligne, colonne, joueur):
    if tableau[ligne][colonne] != "_":
        return False
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    adversaire = "B" if joueur == "N" else "N"
    for dx, dy in directions:
        x, y = ligne + dx, colonne + dy
        trouve_adversaire = False
        while 0 <= x < 8 and 0 <= y < 8 and tableau[x][y] == adversaire:
            trouve_adversaire = True
            x += dx
            y += dy
        if trouve_adversaire and 0 <= x < 8 and 0 <= y < 8 and tableau[x][y] == joueur:
            return True
    return False

# Joue un mouvement
def play_mov(tableau, ligne, colonne, joueur):
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    adversaire = "B" if joueur == "N" else "N"
    tableau[ligne][colonne] = joueur
    for dx, dy in directions:
        x, y = ligne + dx, colonne + dy
        pions_a_retourner = []
        while 0 <= x < 8 and 0 <= y < 8 and tableau[x][y] == adversaire:
            pions_a_retourner.append((x, y))
            x += dx
            y += dy
        if 0 <= x < 8 and 0 <= y < 8 and tableau[x][y] == joueur:
            for px, py in pions_a_retourner:
                tableau[px][py] = joueur

# Liste des mouvements autorisés
def ls_mov_auth(tableau, joueur):
    mouvements = []
    for i in range(8):
        for j in range(8):
            if move_verif(tableau, i, j, joueur):
                mouvements.append((i, j))
    return mouvements

# Évaluation du plateau pour l'IA avec pondération
def evaluer_plateau(tableau, joueur):
    adversaire = "B" if joueur == "N" else "N"
    score_joueur = 0
    score_adversaire = 0
    for i in range(8):
        for j in range(8):
            if tableau[i][j] == joueur:
                score_joueur += PONDERATION[i][j]
            elif tableau[i][j] == adversaire:
                score_adversaire += PONDERATION[i][j]
    return score_joueur - score_adversaire

# Minimax avec Alpha-Bêta Pruning et profondeur
def minimax(tableau, profondeur, joueur, maximisant, alpha=float("-inf"), beta=float("inf")):
    if profondeur == 0 or not ls_mov_auth(tableau, joueur):
        return evaluer_plateau(tableau, "B"), None

    meilleur_score = float("-inf") if maximisant else float("inf")
    meilleur_mouvement = None

    for mouvement in ls_mov_auth(tableau, joueur):
        tableau_copie = [ligne[:] for ligne in tableau]
        play_mov(tableau_copie, mouvement[0], mouvement[1], joueur)
        score, _ = minimax(tableau_copie, profondeur - 1, "B" if joueur == "N" else "N", not maximisant, alpha, beta)

        if maximisant:
            if score > meilleur_score:
                meilleur_score = score
                meilleur_mouvement = mouvement
            alpha = max(alpha, score)
        else:
            if score < meilleur_score:
                meilleur_score = score
                meilleur_mouvement = mouvement
            beta = min(beta, score)

        if beta <= alpha:
            break

    return meilleur_score, meilleur_mouvement

def main():
    tableau = init_plateau()
    joueur_actuel = "N"
    ia_joueur = "B"

    def dessiner_barre_laterale():
        blanc = sum(ligne.count("B") for ligne in tableau)
        noir = sum(ligne.count("N") for ligne in tableau)
        total = blanc + noir
        hauteur_blanche = (blanc / total) * TAILLE_FENETRE if total > 0 else 0
        hauteur_noire = (noir / total) * TAILLE_FENETRE if total > 0 else 0

        pygame.draw.rect(ecran, COULEUR_BLANC, (TAILLE_FENETRE + 10, 0, 40, hauteur_blanche))
        pygame.draw.rect(ecran, COULEUR_NOIR, (TAILLE_FENETRE + 10, hauteur_blanche, 40, hauteur_noire))

    while True:
        ecran.fill((200, 200, 200))  # Fond gris clair pour tout l'écran
        dessiner_plateau(tableau)
        dessiner_barre_laterale()
        pygame.display.flip()

        if joueur_actuel == ia_joueur:
            time.sleep(0.5)
            _, meilleur_mouvement = minimax(tableau, 6, joueur_actuel, True)

            if meilleur_mouvement:
                play_mov(tableau, meilleur_mouvement[0], meilleur_mouvement[1], joueur_actuel)
            joueur_actuel = "B" if joueur_actuel == "N" else "N"
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if x < TAILLE_FENETRE:  # Ignorer les clics sur la barre latérale
                        ligne, colonne = y // TAILLE_CASE, x // TAILLE_CASE
                        if move_verif(tableau, ligne, colonne, joueur_actuel):
                            play_mov(tableau, ligne, colonne, joueur_actuel)
                            joueur_actuel = "B" if joueur_actuel == "N" else "N"

if __name__ == "__main__":
    main()


# Ajout d'une barre latérale pour afficher la répartition des pions
def afficher_barre_laterale(tableau):
    # Calculer la répartition des pions
    total_pions = sum(ligne.count("N") + ligne.count("B") for ligne in tableau)
    if total_pions == 0:
        proportion_noir = proportion_blanc = 0
    else:
        proportion_noir = sum(ligne.count("N") for ligne in tableau) / total_pions
        proportion_blanc = sum(ligne.count("B") for ligne in tableau) / total_pions

    # Dessiner la barre latérale
    largeur_barre = 30
    hauteur_totale = TAILLE_FENETRE

    # Couleur noire
    hauteur_noir = int(hauteur_totale * proportion_noir)
    pygame.draw.rect(ecran, COULEUR_NOIR, (TAILLE_FENETRE, 0, largeur_barre, hauteur_noir))

    # Couleur blanche
    hauteur_blanc = int(hauteur_totale * proportion_blanc)
    pygame.draw.rect(ecran, COULEUR_BLANC, (TAILLE_FENETRE, hauteur_noir, largeur_barre, hauteur_blanc))

# IA avancée avec gestion stratégique des coins et coups d'adversaire
def ia_avancee(tableau, profondeur, joueur, maximisant):
    def valeur_case(ligne, colonne):
        if (ligne, colonne) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
            return 100  # Valeur très élevée pour les coins
        if ligne in [0, 7] or colonne in [0, 7]:
            return 10  # Valeur moyenne pour les bords
        return 1  # Valeur par défaut pour le reste

    if profondeur == 0 or not ls_mov_auth(tableau, joueur):
        return evaluer_plateau(tableau, "B"), None

    meilleur_score = float("-inf") if maximisant else float("inf")
    meilleur_mouvement = None

    for mouvement in sorted(ls_mov_auth(tableau, joueur), key=lambda m: valeur_case(*m), reverse=maximisant):
        tableau_copie = [ligne[:] for ligne in tableau]
        play_mov(tableau_copie, mouvement[0], mouvement[1], joueur)
        score, _ = ia_avancee(tableau_copie, profondeur - 1, "N" if joueur == "B" else "B", not maximisant)

        if maximisant:
            if score > meilleur_score:
                meilleur_score = score
                meilleur_mouvement = mouvement
                print(meilleur_score)
        else:
            if score < meilleur_score:
                meilleur_score = score
                meilleur_mouvement = mouvement

    return meilleur_score, meilleur_mouvement

def main():
    tableau = init_plateau()
    joueur_actuel = "N"
    ia_joueur = "B"

    while True:
        dessiner_plateau(tableau)
        afficher_barre_laterale(tableau)
        pygame.display.flip()

        if joueur_actuel == ia_joueur:
            time.sleep(0.5)
            _, meilleur_mouvement = ia_avancee(tableau, 10, joueur_actuel, True)
            if meilleur_mouvement:
                play_mov(tableau, meilleur_mouvement[0], meilleur_mouvement[1], joueur_actuel)
            joueur_actuel = "N"
            time.sleep(1)
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if x < TAILLE_FENETRE:  # Ignorer les clics sur la barre latérale
                        ligne, colonne = y // TAILLE_CASE, x // TAILLE_CASE
                        if move_verif(tableau, ligne, colonne, joueur_actuel):
                            play_mov(tableau, ligne, colonne, joueur_actuel)
                            joueur_actuel = "B"

if __name__ == "__main__":
    main()
