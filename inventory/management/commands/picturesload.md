# Chargement des images

Idéalement il n'y aurait qu'une image par article. Mais
en pratique ce n'est pas toujours le cas. Nous avons, la plupart du temps,
photographié un article puis nous avons entré son
descriptif. Mais parfois nous avons eu plusieurs
photos décrivant des variantes de coloris.

Cela pose problème pour une création automatique des
objets `Photo` à partir de la liste des photos exportées.

Il est aussi requis que les instances de `Article` définissent
un tri par leur `ID`. Par défaut une requête demandant
tous les articles renvoient une liste dans n'importe
quel ordre.


## Préalable

- Prendre, si possible 1 photo par article et créer la
fiche article correspondante en incluant le No de la photo.

- Ne pas réinitialiser la carte SD. Si possible sélectionner une
numérotation en continu. Tester si la numérotation est continue 
après reformatage de la carte.

## Fonctionnement du script

Le script trie les articles et les photos (champ EXIF `DateTimeOriginal`).
Il relie les 2 listes (fonction `zip`) et crée une ou
plusieurs instances de `Photo` par article.

Afin que le tri fonctionne le script élimine des listes
les articles et les photos déjà créées. 

Pour chaque fichier on extrait la date de création pour
fabriquer une instance `DateTime` qui est ajoutée à la
liste `datetime_list` ainsi que comme
clé du dictionnaire `date_pic` dont la valeur est
le chemin absolue du fichier photo.

La partie `binding` relie les articles aux instances de
`DateTime`, traitant au passage des articles possédant
plusieurs photos.


## Mode d'emploi

1. repérer les articles faisant l'objet de plusieurs
photos et les ajouter au dictionnaire `articles_with_multiple_pic`.
Par exemple:
articles_with_multiple_pic = {141: 14, 142: 12, 143:6, 144:3, 145:3}``
`` où les ID sont les clés.
2. lancer le script. Il va s'arrêter après l'ajout des images de
chaque article. Le relancer autant de fois qu'il y a d'articles.
3. lancer le script en ajustant le nombre total de photos
à traiter dans la variable à la ligne 76: 
``total = 150 # total of articles to handle``
Je recommande de tester avec des petites valeurs, comme 20, et de
commenter la partie créant l'instance de `Photo`.
