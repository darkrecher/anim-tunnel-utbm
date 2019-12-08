class AnimationObject():
    """
    AnimationObject.
    Un élément constituant l'animation.
    Ça peut être quelque chose à afficher à l'écran, ou des sons à jouer,
    ou autre chose.

    À chaque loop de l'animation, le AnimationObject est mis à jour, et peut
    agir sur l'animation.

    L'ordre de traitement des AnimationObject est important, car les éléments affichés
    par l'un d'eux peut être recouvert par l'AnimationObject suivant.

    Les AnimationObject sont tous indépendants. On ne peut pas transmettre de message
    ou de données d'un AnimationObject à un autre.

    Les AnimationObject doivent eux-mêmes initialiser leurs ressources (images, sons,
    données à précalculer, ...) lors de la fonction __init__.
    """


    def __init__(self):
        pass


    def make_loop_action(self, screen, timer_tick):
        """
        À overrider obligatoirement.
        Cette fonction est appelée à chaque tour de boucle.

        Le paramètre screen correspond à l'objet pygame Surface de l'écran.
        Si on effectue des fonctions screen.blit, les éléments blittés s'afficheront
        à l'écran.

        Le paramètre timer_tick est un entier, indiquant la date actuelle de
        l'animation (en tick d'horloge, 50 ticks par seconde).
        """
        raise NotImplemented


    def terminate(self):
        """
        Fonction exécutée à la fin de l'animation.
        Il faut libérer les ressources
        (ou pas, puisque ça se libère tout seul à la fin de l'exécution).
        """
        pass
