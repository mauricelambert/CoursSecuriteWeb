# TP: Premières vulnérabilités Web

## 1. Objectifs du TP

À la fin de ce TP, l'étudiant sera capable de:

* Comprendre l'architecture et le fonctionnement d'une application Web.
* Identifier quelques vulnérabilités affectant les applications Web.
* Comprendre et exploiter des vulnérabilités d'injection.
* Identifier les mesures correctives permettant de protéger ou renforcer une application.
* Connaître l'OWASP Top 10.

---

# 2. Pré-requis

## 2.1 Développement Web

* Connaissances dans un langage backend:

  * PHP
  * Python
  * Java
  * Node.js
  * C#
  * ou équivalent

* Compréhension des concepts suivants:

  * Routage HTTP
  * Gestion des sessions
  * Accès à une base de données
  * Génération dynamique de pages Web

## 2.2 Langages Web

* Syntaxe HTML:

  * Structure d'une page
  * Formulaires
  * Attributs HTML
  * Manipulation du DOM

* Syntaxe JavaScript:

  * Variables et fonctions
  * Manipulation du DOM
  * Événements
  * Requêtes HTTP côté client (Fetch/AJAX)

## 2.3 Réseaux

Connaissances recommandées:

* Comment les couches du réseau fonctionnent, notamment Ethernet/IP/TCP

---

# 3. Qu'est-ce que le Web ?

Le **World Wide Web (WWW)**, ou plus simplement **Web**, est un système d'information distribué fonctionnant au-dessus d'Internet. Il permet d'accéder à des ressources (pages, images, vidéos, documents, API, etc.) identifiées par une **URI (Uniform Resource Identifier)** et reliées entre elles par des **liens hypertextes**.

Le Web repose sur plusieurs couches techniques:

| Couche   | Rôle                                                        |
| -------- | ----------------------------------------------------------- |
| Réseau   | Transmission des données (Ethernet, Wi-Fi, etc.)            |
| Internet | Acheminement des paquets (IP) et transport (TCP dans ce TP) |
| Web      | Échange de ressources via le protocole HTTP(S)              |

## 3.1 Le fonctionnement d'une application Web

Une application Web repose généralement sur deux composants principaux:

 - Le client: il s'agit le plus souvent du navigateur Web (Firefox, Chrome, Edge, etc.), utilisé par l'utilisateur pour consulter et manipuler l'application.
 - Le serveur: il reçoit les requêtes du client, exécute la logique applicative, accède éventuellement à une base de données et renvoie les réponses nécessaires au fonctionnement de l'application.

Le client et le serveur communiquent principalement à l'aide du protocole HTTP, ou de sa version sécurisée HTTPS.

### 3.1.1 Le rôle du serveur

Le serveur héberge tout ou partie de l'application Web. Il peut notamment:

 - recevoir et analyser les requêtes HTTP;
 - vérifier l'identité d'un utilisateur;
 - contrôler les permissions associées à cet utilisateur;
 - exécuter la logique métier de l'application;
 - lire ou modifier des données dans une base de données;
 - générer du contenu HTML;
 - fournir des données à une interface Web, généralement au format JSON (JavaScript Object Notation).

Par exemple, lorsqu'un utilisateur se connecte à une application, le serveur peut vérifier les identifiants transmis, rechercher le compte correspondant dans la base de données et créer une session permettant de reconnaître l'utilisateur lors de ses prochaines requêtes.

Le serveur peut également appliquer des règles de sécurité : vérifier qu'un utilisateur a le droit de consulter une ressource, limiter les données accessibles ou refuser une opération non autorisée.

Le serveur constitue donc un point central pour l'application des règles de sécurité. Les décisions importantes ne doivent pas dépendre uniquement du comportement du navigateur.

### 3.1.2 Le rôle du client

Le client, généralement le navigateur Web, est chargé de présenter l'application à l'utilisateur et de lui permettre d'interagir avec elle.

Il interprète notamment:

 - **HTML**, qui définit la structure et le contenu de la page;
 - **CSS**, qui décrit sa présentation visuelle;
 - **JavaScript**, qui permet d'ajouter des comportements interactifs et de communiquer avec le serveur.

Le serveur peut transmettre ces fichiers au navigateur, qui les interprète ou les exécute localement.

Par exemple, lorsqu'un utilisateur ouvre une page contenant un formulaire, le navigateur affiche les champs de saisie et peut vérifier que certains champs sont remplis avant l'envoi. JavaScript peut également actualiser une partie de la page sans nécessiter son rechargement complet.

Le navigateur peut aussi envoyer de nouvelles requêtes HTTP pour récupérer des informations ou demander au serveur d'effectuer une opération.

Il est important de comprendre que **le navigateur ne se contente pas d'afficher des pages: il exécute également une partie du code de l'application**.

### 3.2.3 Exemple: le chargement d'une page Web

Considérons un utilisateur qui souhaite accéder à une application disponible à l'adresse https://www.exemple.fr.

Le fonctionnement simplifié est le suivant:

1. L'utilisateur saisit l'adresse dans son navigateur.
2. Le navigateur envoie une requête HTTP au serveur.
3. Le serveur reçoit la requête et détermine la ressource demandée.
4. Le serveur renvoie une réponse contenant, par exemple, du HTML.
5. Le navigateur interprète le HTML et affiche la page.
6. Si le document référence des fichiers CSS, JavaScript ou des images, le navigateur peut envoyer des requêtes supplémentaires pour les récupérer.
7. Le navigateur interprète ces ressources afin de construire et de rendre la page interactive.

Le schéma suivant illustre ce fonctionnement:

```
              CLIENT                              SERVEUR
        ┌─────────────────┐                ┌─────────────────┐
        │    Navigateur   │                │  Application    │
        │                 │                │  backend        │
        │       URL       │                │                 │
        └────────┬────────┘                └────────┬────────┘
                 │                                  │
                 │       Requête HTTP               │
                 │ ────────────────────────────────>│
                 │                                  │
                 │                       Traitement de la
                 │                       requête et accès
                 │                       éventuel à la BDD.
                 |                       Génération de la page
                 |                       HTML, CSS et JavaScript
                 │                                  │
                 │       Réponse HTTP               │
                 │ <────────────────────────────────│
                 │                                  │
        ┌────────▼────────┐                ┌────────▼────────┐
        │ Interprétation  │                │ Base de données │
        │ et affichage    │                │ (si nécessaire) │
        |                 |                |                 |
        | HTML / CSS / JS |                |                 | 
        └─────────────────┘                └─────────────────┘
```

Dans une application, les communications avec la base de données sont généralement effectuées par le backend, et rarement par le navigateur (indirectement avec des outils comme firebase / supabase).

## 3.2 Le navigateur: un environnement d'exécution isolé

Le navigateur exécute du code provenant de différentes ressources Web. Il doit cependant empêcher, autant que possible, qu'une page Web puisse accéder librement aux données et aux ressources du système de l'utilisateur.

Pour cela, il met en œuvre plusieurs mécanismes de sécurité, dont la **sandbox** (*environnement d'exécution isolé*).

### 3.2.1 Le principe de la sandbox

Une sandbox limite les actions qu'un programme peut effectuer et les ressources auxquelles il peut accéder.

Dans le contexte du Web, le code JavaScript d'une page s'exécute dans un environnement contrôlé par le navigateur. Il ne dispose pas, par défaut, d'un accès arbitraire au système de fichiers, aux processus ou aux ressources internes de l'ordinateur.

Par exemple, un script JavaScript exécuté dans une page Web ne peut pas simplement lire tous les fichiers personnels de l'utilisateur ou exécuter librement des commandes système.

Certaines fonctionnalités peuvent toutefois être accessibles sous conditions, notamment lorsque le navigateur demande une autorisation à l'utilisateur (accès au microphone, caméra, haut-parleur, ...).

Ces protections ne signifient pas qu'un navigateur est invulnérable. Une faille du navigateur peut notamment compromettre certaines de ces garanties.

### 3.2.2 Pourquoi ce mécanisme est-il important ?

Une application Web peut charger du code provenant d'un serveur distant, parfois sans que l'utilisateur en connaisse précisément le contenu.

Sans mécanismes d'isolation, la simple visite d'une page Web pourrait présenter des risques beaucoup plus importants pour le système du client.

La sandbox permet donc de limiter les conséquences potentielles de l'exécution de code Web.

Il faut néanmoins distinguer deux choses:

 - **La sécurité du système du client**: elle dépend notamment des protections du navigateur et du système d'exploitation.
 - **La sécurité de l'application Web**: elle dépend également du code client, du backend, des mécanismes d'authentification et d'autorisation, ainsi que de la protection des données.

Une application Web peut être vulnérable même si le navigateur isole correctement son code du système d'exploitation.

## 3.3 La séparation des responsabilités entre client et serveur

Lors du développement d'une application Web, il est recommandé de répartir les responsabilités entre le client et le serveur.

Cette séparation permet de simplifier le développement et de limiter les risques de sécurité.

### 3.3.1 Les responsabilités du client

Le client est principalement responsable de l'interface utilisateur et de son fonctionnement.

Il peut notamment:

 - afficher les informations reçues du serveur;
 - organiser la présentation des données;
 - gérer les interactions avec l'utilisateur;
 - effectuer des vérifications de saisie pour améliorer l'expérience utilisateur;
 - envoyer des requêtes au serveur;
 - mettre à jour l'interface en fonction des réponses reçues.

Par exemple, un formulaire peut vérifier qu'un champ obligatoire n'est pas vide avant de transmettre les données.

Cependant, ces vérifications côté client ont principalement un objectif ergonomique. Elles peuvent être modifiées, contournées ou supprimées par un utilisateur qui contrôle son navigateur.

**Une validation effectuée uniquement côté client ne constitue donc jamais une protection suffisante.**

### 3.3.2 Les responsabilités du serveur

Le serveur est responsable des traitements sensibles et de l'application effective des règles de sécurité.

Il doit notamment:

 - vérifier les données reçues;
 - authentifier les utilisateurs lorsque cela est nécessaire;
 - contrôler les autorisations pour chaque opération protégée;
 - appliquer les règles métier;
 - accéder aux données protégées;
 - protéger les secrets et les identifiants de connexion;
 - effectuer les opérations en base de données ou sur le système de manière sécurisée.

Prenons l'exemple d'une application permettant à chaque utilisateur de consulter son profil.

Le navigateur peut envoyer une requête demandant les informations d'un utilisateur. Le serveur doit vérifier que l'utilisateur connecté est autorisé à consulter ce profil.

Il ne suffit pas de masquer les profils des autres utilisateurs dans l'interface: un utilisateur pourrait modifier directement la requête HTTP envoyée au serveur.

> Une requête HTTP, c'est avant tout des données, elles sont structurées pour suivre les règles du protocole. Vous pouvez modifier TOUTE la requête, faire en sorte qu'elle ne respecte pas le protocole, car c'est vous qui choisissez ce que vous envoyez.
>> Le navigateur crée pour vous ces données dans la bonne structure. Vous pouvez utiliser n'importe quel `socket` TCP pour envoyer les données que vous souhaitez.

> Vous pouvez modifier la requête en conservant le format du protocole HTTP, de cette manière vous pourriez envoyer la même requête que le navigateur de votre voisin (ou n'importe quelle autre requête), dans la plupart des cas cela pourrait vous faire passer pour le navigateur usurpé auprès du serveur. On utilise des données **aléatoires et secrètes** sur des **flux chiffrés** pour éviter l'usurpation.

La vérification des autorisations doit donc être effectuée côté serveur, à chaque accès pertinent à une ressource.

### 3.3.3 Exemple: validation d'un formulaire

Imaginons un formulaire d'inscription demandant un nom d'utilisateur et un mot de passe.

La validation côté client peut vérifier que:

 - les champs obligatoires sont remplis;
 - le mot de passe respecte une longueur minimale;
 - les données ont un format cohérent.

Le serveur doit néanmoins effectuer ses propres vérifications avant de traiter la demande. Il ne peut pas supposer que les contrôles du navigateur ont été exécutés ou respectés.

| Vérification | Côté client | Côté serveur |
| --- | --- | --- |
| Vérifier qu'un champ est rempli | Oui, pour le confort de l'utilisateur | Oui, pour garantir la règle |
| Vérifier le format des données | Oui, pour fournir un retour rapide | Oui, avant le traitement |
| Vérifier l'identité de l'utilisateur | Non, pas de manière fiable à lui seul | Oui |
| Vérifier les autorisations d'accès | Non, pas de manière fiable à lui seul | Oui |
| Protéger les identifiants de base de données | Non | Oui, dans une architecture backend classique |
| Appliquer les règles métier sensibles | Peut contribuer à l'interface | Oui |

Les contrôles côté client améliorent l'expérience utilisateur, tandis que les contrôles côté serveur garantissent que les règles de sécurité sont effectivement appliquées.

## 3.4 Accès aux données : backend classique et services BaaS

Dans une architecture Web classique, le navigateur ne se connecte généralement pas directement à la base de données.

Le backend sert d'intermédiaire entre le client et les données.

Cette architecture permet notamment au backend de contrôler les accès aux données, d'appliquer les règles métier et de protéger les identifiants de connexion à la base de données.

### 3.4.1 Le cas de Firebase et Supabase

Certains services, comme Firebase et Supabase, proposent une architecture différente, souvent désignée par le terme **BaaS** (_Backend as a Service_).

Ils exposent des fonctionnalités backend au moyen de SDK et d'API accessibles directement depuis le navigateur.

Dans ce modèle, le client peut effectuer certaines opérations sur les données sans passer par un backend applicatif développé spécifiquement pour chaque requête.

Cela ne signifie pas que les données sont nécessairement publiques ni que la sécurité est prise en charge automatiquement.

Il faut notamment configurer correctement:

- les règles de sécurité de Firebase, par exemple les _Firestore Security Rules_ ;
- les politiques d'accès de Supabase, notamment la _Row Level Security_ (RLS) de PostgreSQL ;
- les mécanismes d'authentification et d'autorisation ;
- les permissions associées aux clés et aux différents services.

Une clé destinée à être utilisée dans le navigateur n'est pas nécessairement un secret. À l'inverse, une clé privilégiée permettant de contourner les contrôles d'accès ne doit pas être exposée au client.

**Le principe reste identique: les contrôles de sécurité doivent être appliqués par le composant qui protège réellement la ressource, et non uniquement par l'interface utilisateur.**

## 3.4 Les ressources Web

Une ressource Web peut être de différentes natures:

* une page HTML;
* une image;
* une feuille de style CSS;
* un script JavaScript;
* un fichier téléchargeable;
* un flux audio ou vidéo;
* une réponse d'API (JSON, XML, etc.).

Chaque ressource est identifiée par une **URI** (*Uniform Resource Identifier*). Dans la pratique, on utilise principalement des **URL** (*Uniform Resource Locator*), qui indiquent où se trouve une ressource et comment y accéder.

Exemple:

```text
https://www.exemple.fr/images/logo.png
```

Une URL est composée de plusieurs éléments:

```text
https://www.exemple.fr:443/images/logo.png?version=2#presentation
└─┬─┘  └──────┬──────┘ └┬┘ └──────┬──────┘ └───┬───┘ └─────┬─────┘
protocole   domaine   port      chemin     paramètres   fragment
```

### Le protocole

Le protocole indique la méthode utilisée pour accéder à la ressource.

Exemples:

* `http` : communication non chiffrée;
* `https` : communication HTTP protégée par TLS;
* `ftp` : transfert de fichiers.

Pour les applications Web modernes, HTTP et HTTPS sont les protocoles principalement utilisés.

### Le domaine

Le domaine identifie le serveur qui héberge la ressource.

Exemple:

```text
www.exemple.fr
```

Il est associé à une adresse IP grâce au système DNS (*Domain Name System*).

### Le port

Le port indique le service réseau utilisé.

Ports courants:

| Port | Service |
| ---- | ------- |
| 80   | HTTP    |
| 443  | HTTPS   |

Lorsqu'il utilise le port par défaut, celui-ci est généralement omis dans l'URL.

Exemple:

```text
https://www.exemple.fr
```

correspond implicitement à:

```text
https://www.exemple.fr:443
```

### Le chemin

Le chemin identifie une ressource sur le serveur.

Exemples:

```text
/images/logo.png
/users/profile.html
/api/users
```

Dans une application Web dynamique, le chemin peut correspondre à une route traitée par l'application backend et non forcément à un fichier réel.

Exemple:

```text
https://www.exemple.fr/users/42
```

peut être traité par l'application afin d'afficher le profil de l'utilisateur ayant l'identifiant `42`.

### Les paramètres

Les paramètres permettent de transmettre des informations supplémentaires au serveur.

Ils commencent par le caractère `?` et sont séparés par `&`.

Exemple:

```text
https://www.exemple.fr/recherche?q=securite&page=2
```

Ici:

```text
q=securite
page=2
```

sont deux paramètres envoyés au serveur.

Ces paramètres doivent être considérés comme des données non fiables et contrôlés côté serveur.

### Le fragment

Le fragment commence par le caractère `#`.

Exemple:

```text
https://www.exemple.fr/document.html#chapitre3
```

Il est généralement utilisé pour naviguer dans une page ou gérer l'état d'une application côté navigateur.

Contrairement aux paramètres, le fragment n'est pas envoyé au serveur lors d'une requête HTTP classique.

---

Une page Web est généralement composée de plusieurs ressources téléchargées séparément par le navigateur:

```text
Page HTML
   |
   +-- style.css
   |
   +-- script.js
   |
   +-- image.png
   |
   +-- requêtes API
```

Lors du chargement d'une page, le navigateur analyse le document HTML puis effectue automatiquement les requêtes nécessaires pour récupérer ces différentes ressources.

## 3.5 Les technologies du Web

Une application Web moderne repose principalement sur trois langages complémentaires.

### HTML

Le **HTML (HyperText Markup Language)** décrit la structure d'une page:

* titres;
* paragraphes;
* images;
* formulaires;
* liens hypertextes;
* tableaux.

Le HTML est un **langage de balisage** (markup language). Il décrit le contenu mais ne définit pas son apparence.

### CSS

Le **CSS (Cascading Style Sheets)** définit la présentation de la page:

* couleurs;
* polices;
* marges;
* disposition des éléments;
* mise en page responsive.

Il permet de séparer le contenu de sa présentation.

### JavaScript

Le **JavaScript** apporte le comportement dynamique d'une application Web:

* interactions avec l'utilisateur;
* modification du contenu de la page;
* communication avec le serveur (AJAX / Fetch);
* validation de formulaires;
* interfaces interactives.

## 3.6 HTML: du texte interprété

Le HTML est un fichier texte contenant des balises décrivant la structure d'un document. Contrairement à un programme compilé, son contenu est directement interprété par le navigateur.

Par exemple:

```html
<!DOCTYPE html>
<html>
    <head>
        <title>Ma première page</title>
    </head>

    <body>
        <h1>Bonjour</h1>
        <p>Bienvenue sur cette page.</p>
    </body>
</html>
```

Le navigateur interprète ce document pour afficher une page Web lisible par l'utilisateur.

Comme il s'agit simplement de texte, il est possible d'afficher le code source d'une page Web et de comprendre une partie de son fonctionnement.

> **Remarque:** HTML s'inspire historiquement de SGML. XHTML, une variante plus stricte de HTML, est quant à lui une application de XML. Le HTML5 moderne n'est cependant pas basé sur XML et utilise ses propres règles de syntaxe.

## 3.7 Inspection d'une page Web

Les navigateurs modernes permettent d'accéder au **code source** d'une page à l'aide du raccourci **Ctrl+U** (ou via le menu contextuel « Afficher le code source de la page »). Ils proposent également des **outils de développement** (*Developer Tools*), accessibles généralement avec la touche **F12** ou le raccourci **Ctrl+Maj+I**.

Ces outils permettent notamment de:

* consulter le code HTML généré;
* afficher les feuilles de style CSS;
* observer le code JavaScript exécuté;
* visualiser les requêtes HTTP;
* inspecter les cookies et le stockage local.

Ces fonctionnalités sont intéressantes lors d'un audit de sécurité.

## Exercice 1

1. Ouvrir le site suivant: [https://XXXX.XXX/](https://XXXX.XXX/)
2. Rechercher le **flag** caché dans le code source de la page.

## Exercice 2

1. Ouvrez les outils de développement puis sélectionnez l'onglet **Console**.
2. Exécutez la *commande* suivante: `alert(atob("RkxBR3tKYVZhU2NSaVB0X0lTX0lOQ1JFRElCTEUhfQ=="));`

## Exercice 3

Dans cet exercice, vous allez créer une page Web simple et observer que le contenu affiché n'est pas forcément écrit directement dans le fichier HTML.

1. Ouvrez votre éditeur de texte.
2. Créez un fichier nommé `index.html`.
3. Copiez-collez le code suivant:

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Exercice HTML</title>
</head>

<body>

<h1>Exercice 3</h1>

<div id="flag"></div>

<script>
const codes = [70, 76, 65, 71, 123, 72, 84, 77, 76, 95, 73, 83, 95, 73, 78, 84, 69, 82, 80, 82, 69, 84, 69, 68, 125];
let flag = "";
for (const c of codes) {
    flag += String.fromCharCode(c);
}
document.getElementById("flag").textContent = flag;
</script>

</body>
</html>
```

4. Enregistrez le fichier.
5. Ouvrez-le dans votre navigateur.

---

# 4. Introduction aux applications Web

## 4.1 Architecture générale

Une application Web repose sur plusieurs composants:

```
Client (par exemple le navigateur)
 |
 | HTTP/HTTPS
 |
[Optionnel : CDN, WAF, reverse proxy, load balancer, IDS/IPS, firewall]
 |
Serveur Web
 |
[OPTIONNEL: framework, middleware]
 |
Application Backend
 |
[Optionnel : base de données, cache, services externes, API]
```

Chaque couche peut être impactée par des vulnérabilités:

| Composant       | Exemples de risques         |
| --------------- | --------------------------- |
| Navigateur      | XSS, vol de session         |
| Proxy           | Attaque sur le cache        |
| Serveur Web     | Mauvaise configuration      |
| Backend         | Injection, contrôle d'accès |
| Base de données | Fuite de données            |
| Dépendances     | Composants vulnérables      |

## Exercice 4

1. Copiez-collez le code suivant dans un fichier nommé: `server.py` puis lancez le script avec la commande: `python3 server.py`
2. Le service est joignable en `HTTP`, il est lancé sur le "domaine" `localhost` et sur le port `8080` et avec le chemin: `/challenge1`. Trouvez le flag.

Le code (ce serveur héberge les exercices 4 à 10):

```

```

---

# 5. Fonctionnement du protocole HTTP

## 5.1 Structure d'une requête HTTP

Une requête HTTP contient:

* Une méthode:

  * GET
  * POST
  * PUT
  * PATCH
  * DELETE
  * HEAD
  * OPTIONS
  * TRACE
  * CONNECT

* Une URL ou le chemin (*path*) et les paramètres (*query*) de l'URL

  * `/`
  * `/users`
  * `/users?filter=toto`

* Des en-têtes HTTP

  * `Cookie: session=abc`
  * `Host: example.com`

* Un corps de requête éventuel (tout le contenu/données à envoyer)

Exemple:

```
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 27

username=test&password=test
```

---

## 5.2 Les headers HTTP importants en sécurité

### Content-Security-Policy (CSP)

Objectif:

* Limiter les sources de contenu exécutables.
* Réduire l'impact des attaques XSS.

Exemple:

```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

---

### Cookie flags: HttpOnly & Secure & SameSite

Attribut d'un cookie empêchant l'accès JavaScript, l'envoi des cookies sur des flux non chiffrés et l'envoi des cookies lors des requêtes externes:

```
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict
```

Protection contre:

* Vol de cookie via XSS.
* Interception sur un réseau non sécurisé.
* Certaines attaques CSRF.

---

### Autres headers importants

#### X-Content-Type-Options

Empêche le navigateur de deviner un type MIME:

```
X-Content-Type-Options: nosniff
```

#### Strict-Transport-Security (HSTS)

Force l'utilisation de HTTPS:

```
Strict-Transport-Security: max-age=31536000
```

#### Referrer-Policy

Limite la fuite d'informations via le header Referer.

#### Permissions-Policy

Contrôle l'accès aux fonctionnalités du navigateur.

## Exercice 5

Votre ami vous a fourni une URL avec authentification pour accéder à une donnée secrète, malheureusement il a dû se tromper dans l'URL car les données d'authentification ne semblent pas arriver jusqu'au serveur... En comprenant le fonctionnement du protocole HTTP et l'interprétation de l'URL corrigez l'erreur.

> L'identifiant et le mot de passe sont corrects, le chemin, le protocole ainsi que le nom du serveur et le port sont également corrects.

Voici l'URL: http://localhost:8080/#admin:pass

## Exercice 6

Cette fois le flag n'est plus caché dans la page HTML, cette fois il est dans la communication HTTP, serez-vous capable de le retrouver ?

## Exercice 7

Et lorsque le serveur HTTP est non conforme ? Serez-vous capable de requêter le serveur avec la méthode `FLAG` et le *Host* à `flag.local` ?

---

## 5.3 Structure d'une réponse HTTP

**TODO**

---

# 6. Principes fondamentaux de sécurité Web

Les applications web utilisent des contextes complexes: client, serveur web, application, base de données, API externes, ...

Afin de produire un contenu dynamique (par exemple une même interface permettant de vendre plusieurs produits, d'afficher différents profils utilisateurs ou encore les messages privés de chaque compte), l'application doit **générer du code HTML**.
De même, pour requêter une base de données il faut utiliser un langage (SQL pour les bases de données relationnelles) et que les requêtes doivent différer entre les différents utilisateurs pour n'obtenir que les informations auxquelles l'utilisateur a le droit d'accéder. L'application doit donc **générer la requête à partir des informations fournies par l'utilisateur**.

Si un programme, génère du code qui sera exécuté par la suite à partir de données utilisateur alors il peut être vulnérable aux injections s'il est mal sécurisé. Un utilisateur malveillant pourrait fournir des données spécialement construites afin qu'elles soient interprétées comme des instructions et modifient le comportement attendu du programme.

## 6.1 Ne jamais faire confiance aux données utilisateur

Toutes les données externes doivent être considérées comme non fiables:

* URL: chemin (*path*), paramètres (*query*)
* Corps/contenu de la requête
* Méthode et en-têtes HTTP (*Host*, *Referrer*, *Cookie*, ...)
* Données provenant d'API externes

---

## 6.2 Validation des entrées

Objectif: Vérifier qu'une donnée correspond au format attendu.

Exemples:

* Une date doit être une date valide.
* Un identifiant doit respecter un format précis.
* Un nombre doit être compris dans un intervalle.

---

## 6.3 Encodage des sorties

Principe:

> Valider les entrées, encoder les sorties.

Permet de limiter:

* Cross-Site Scripting (XSS)
* Injection HTML

Exemple:

Donnée:

```
<script>alert(1)</script>
```

Affichage sécurisé:

```
&lt;script&gt;alert(1)&lt;/script&gt;
```

| Le programme construit... | Interprété par...      | Vulnérabilité possible |
| ------------------------- | ---------------------- | ---------------------- |
| HTML                      | Navigateur             | XSS                    |
| SQL                       | Base de données        | SQL Injection          |
| Commande système          | Système d'exploitation | Command Injection      |
| Requête LDAP              | Serveur LDAP           | LDAP Injection         |
| Expression de template    | Moteur de templates    | SSTI                   |
| Requête XPath             | Moteur XPath           | XPath Injection        |

---

## 6.4 Authentification

Bonnes pratiques:

* Ne jamais stocker les mots de passe en clair.

* Utiliser un algorithme de hash adapté:

  * Argon2
  * bcrypt
  * scrypt
  * PBKDF2-HMAC-SHA-256 ou SHA-512

* Utiliser:

  * Utiliser une authentification multifacteur (MFA) robuste lorsque cela est possible
  * Limitation des tentatives
  * Gestion correcte des sessions

---

## 6.5 Gestion des sessions

Recommandations:

* Utiliser des identifiants de session aléatoires.
* Expirer les sessions.
* Régénérer l'identifiant après authentification.
* Protéger les cookies avec:

  * HttpOnly
  * Secure
  * SameSite

---

## 6.6 Protection CSRF

Principe: Une requête malveillante peut être envoyée depuis un autre site.

Protection:

* Token CSRF unique par session.
* Vérification du header Origin.
* Cookie SameSite.

---

## Exercice 8

Trouvez le mot de passe de l'utilisateur `admin` du `/challenge5`.

## Exercice 9

1. Authentifiez-vous sur le `/challenge6` avec `admin` et `pass`.
2. Injectez une balise `script` dans la page HTML `home`.

> Comment le serveur peut-il bien connaître votre nom d'utilisateur alors que vous n'envoyez plus les données d'authentification ?

---

# 7. Comprendre les vulnérabilités d'injection les plus courantes

Tous les flux de données peuvent être concernés par des vulnérabilités par injection dès lors qu'ils sont interprétés selon une syntaxe définie. Pour extraire les informations d'un flux textuel, un _parser_ (analyseur syntaxique) reconnaît des tokens à partir de caractères spécifiques, notamment les délimiteurs, dont l'interprétation est définie par une grammaire. Si un utilisateur peut injecter ces caractères sans filtrage adapté, il peut introduire de nouveaux tokens dans le flux, qui seront interprétés si la syntaxe et la grammaire le permettent. Ainsi, lorsqu'un programme génère un flux destiné à être interprété à partir de données contrôlées par un utilisateur, un filtrage absent ou insuffisant des entrées ou des sorties peut permettre à un attaquant de modifier la structure ou la sémantique du flux et, potentiellement, de détourner son interprétation. C'est le principe général des vulnérabilités par injection, comme les injections SQL, HTML ou de commandes système.

## 7.1 Base de données relationnelle

> Une base de données relationnelle organise les informations dans des *tables* composées de *lignes (enregistrements)* et de *colonnes (attributs)*. Les données sont manipulées grâce au langage **SQL (Structured Query Language)**.

Une table de base de données peut être représentée ainsi:

```
utilisateurs
+----+----------+----------------+
| id | username | password       |
+----+----------+----------------+
| 1  | admin    | ********       |
| 2  | alice    | ********       |
| 3  | bob      | ********       |
+----+----------+----------------+
```

| Notion        | Description                                                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Table         | Ensemble d'enregistrements décrivant un même type d'objet (proche d'une classe en POO).                                         |
| Ligne         | Un enregistrement représentant une instance (proche d'un objet en POO).                                                         |
| Colonne       | Une propriété commune à tous les enregistrements (proche d'un attribut).                                                        |
| Clé primaire  | Colonne (ou ensemble de colonnes) identifiant de manière unique un enregistrement.                                              |
| Clé étrangère | Colonne faisant référence à la clé primaire d'une autre table afin de représenter une relation entre deux ensembles de données. |

Exemple:

```sql
SELECT * FROM utilisateurs;
```

```sql
INSERT INTO utilisateurs(username) VALUES ('alice');
```

```sql
UPDATE utilisateurs SET username='bob' WHERE id=1;
```

```sql
DELETE FROM utilisateurs WHERE id=3;
```

Lorsqu'un utilisateur saisit son identifiant et son mot de passe, l'**application construit une requête SQL** afin de rechercher l'utilisateur correspondant dans la base de données.

```sql
SELECT id FROM utilisateurs WHERE username = '{username}' AND password = '{hashed_password}';
```

Historiquement, la première défense consistait à **échapper** (*escaping*) les caractères spéciaux afin qu'ils ne soient plus interprétés comme des éléments du langage SQL.

Par exemple, avec une telle fonction, le username:

 - `admin'1` devient `admin\'1`
 - `admin\1` devient `admin\\1`.

Cette approche s'est révélée difficile à appliquer correctement: il suffisait qu'un développeur oublie d'échapper une valeur ou construise une partie de la requête différemment pour réintroduire une vulnérabilité.

Afin d'éviter les vulnérabilités d'injection, il est recommandé de ne plus **insérer directement** les valeurs dans les requêtes, mais d'utiliser des **requêtes préparées**.

Les **requêtes préparées** séparent les instructions SQL des données. La requête est d'abord analysée par le moteur de base de données, puis les paramètres sont transmis séparément. Leur contenu est alors toujours interprété comme des données, quel que soit leur format.

Par exemple:

```sql
SELECT id FROM utilisateurs WHERE username = ? AND password = ?;
```

```
Paramètre 1: admin
Paramètre 2: pass
```

C'est le moteur de base de données qui associe les paramètres à la requête en garantissant qu'ils seront toujours interprétés comme des données.

### À retenir :

> Une requête SQL est une instruction destinée à être interprétée par le moteur de base de données. Si une application construit cette instruction en y insérant directement des données contrôlées par un utilisateur, elle peut devenir vulnérable à une **injection SQL**. Les requêtes préparées permettent de **distinguer les instructions des données**, empêchant ainsi qu'une donnée soit interprétée comme du code SQL.

Points de sécurité:

* Utiliser des requêtes préparées.
* Ne jamais concaténer une entrée utilisateur dans une requête SQL.
* Appliquer le principe du moindre privilège aux comptes SQL.

---

## 7.2 JavaScript

> JavaScript est le langage exécuté par le navigateur. Il permet de modifier le contenu de la page, de réagir aux actions de l'utilisateur et de communiquer avec le serveur sans recharger la page.

Le **DOM (Document Object Model)** est une représentation de la page Web sous forme d'arbre. Chaque élément HTML devient un objet que JavaScript peut lire ou modifier.

```
document
│
├── html
│   ├── head
│   └── body
│       ├── h1
│       ├── p
│       └── div
```

Lorsqu'une application construit une page HTML à partir de données fournies par un utilisateur, elle doit **distinguer le contenu du code HTML**. Si des données utilisateur sont interprétées comme du HTML ou du JavaScript, un attaquant peut modifier le comportement de la page.

### Exemples:

Obtenir un élément:

```javascript
const titre = document.getElementById("titre");
```

Modifier son texte:

```javascript
titre.textContent = "Bonjour";
```

Modifier le contenu HTML:

```javascript
titre.innerHTML = "<b>Bonjour</b>";
```

Les méthodes qui interprètent une chaîne de caractères comme du HTML peuvent introduire une vulnérabilité **Cross-Site Scripting (XSS)** lorsqu'elles reçoivent des données contrôlées par un utilisateur. Dans ce cas, le navigateur ne distingue plus les données du code HTML ou JavaScript et peut exécuter des instructions injectées par un attaquant.

```javascript
const url = new URL(window.location.href);
titre.innerHTML = "<h1>" + url.search + "</h1>";
```

Il est recommandé de construire les éléments HTML avec les APIs javascript et d'ajouter du contenu texte ensuite, exemple:

```javascript
const url = new URL(window.location.href);
const titre = document.createElement("h1");
titre.textContent = url.search;
document.body.appendChild(titre);
```

| Méthode           | Interprète du HTML     |     Risque XSS |
| ----------------- | ---------------------- | -------------: |
| `textContent`     | Non                    |         Faible |
| `innerText`       | Non                    |         Faible |
| `setAttribute()`* | Non (selon l'attribut) | Faible à moyen |
| `innerHTML`       | Oui                    |          Élevé |

> `eval()` interprète une chaîne de caractères comme du code JavaScript. Son utilisation est **fortement déconseillée** car elle peut conduire à l'exécution de code fourni par un utilisateur.

### À retenir:

> Une page HTML est interprétée par le navigateur. Si une application construit cette page en y insérant directement des données contrôlées par un utilisateur, celles-ci peuvent être interprétées comme du code HTML ou JavaScript. Les méthodes telles que `textContent` permettent de **distinguer les données du code HTML**, limitant ainsi les risques de **Cross-Site Scripting (XSS)**.

Points de sécurité:

* Attention aux manipulations du DOM.
* Éviter l'utilisation dangereuse de:

  * innerHTML
  * eval()

* Préférer :

  * textContent
  * méthodes d'encodage

---

## Exercice 10

Dans le `/challenge7`, trouvez le mot de passe de l'utilisateur caché.

## 7.3 Bonnes pratiques

**TODO** -> SAST / DAST

---

# 8. OWASP Top 10

L'**OWASP** (*Open Worldwide Application Security Project*) est une organisation à but non lucratif dont l'objectif est d'améliorer la sécurité des applications. Elle publie gratuitement des guides, des méthodologies, des outils et des recommandations destinés aux développeurs, aux administrateurs système et aux auditeurs de sécurité.

L'une de ses publications les plus connues est l'**OWASP Top 10**, un classement des principales catégories de vulnérabilités rencontrées dans les applications Web. Ce document est régulièrement mis à jour afin de refléter l'évolution des technologies et des menaces. Il constitue aujourd'hui une référence largement utilisée dans les domaines du développement sécurisé, de l'audit et des tests d'intrusion.

Ce TP s'appuie sur l'**OWASP Top 10:2025** afin de structurer les différents types de vulnérabilités étudiés. Une catégorie présente dans la version **2021** (*A10 – Server-Side Request Forgery*) est également abordée, car elle reste fréquemment rencontrée dans les applications existantes, les outils d'audit et les supports de formation.

## A01 - Broken Access Control

Objectif: Vérifier que les utilisateurs ne peuvent accéder qu'aux ressources autorisées.

Points de contrôle:

* Vérification serveur des permissions.
* Séparation des rôles.
* Protection des API.

---

## A02 - Security Misconfiguration

Points de contrôle:

* Services inutiles désactivés.
* Messages d'erreur non verbeux.
* Headers de sécurité présents.
* Configuration HTTPS correcte.

---

## A03 - Software Supply Chain Failures

Points de contrôle:

* Dépendances utilisées.
* Versions vulnérables.
* Utilisation de sources de confiance pour les bibliothèques et dépendances.

---

## A04 - Cryptographic Failures

Points de contrôle:

* Utilisation correcte de HTTPS.
* Protection des données sensibles.
* Hashage correct des mots de passe.

---

## A05 - Injection

Inclut :

* XSS
* SQL Injection
* NoSQL Injection
* Command Injection
* LDAP Injection
* Template Injection (SSTI)

Protections :

* Requêtes paramétrées.
* Validation des entrées.
* Séparation données / commandes.

---

## A06 - Insecure Design

Points de contrôle:

* Présence d'une analyse de risques.
* Gestion correcte des scénarios abusifs.
* Principe du moindre privilège.

---

## A07 - Authentication Failures

Points de contrôle:

* Politique de mot de passe.
* Gestion des sessions.
* Protection contre le brute-force.

---

## A08 - Software or Data Integrity Failures

Points de contrôle:

* Vérification des mises à jour.
* Validation des fichiers importés.
* Sécurité du pipeline de développement.

---

## A09 - Security Logging and Alerting Failures

Points de contrôle:

* Présence de logs.
* Détection des événements suspects.
* Conservation adaptée des traces.

---

## A10 - Mishandling of Exceptional Conditions

Points de contrôle:

* Gestion correcte des erreurs.
* Pas de fuite d'informations.
* Gestion des cas inattendus.

---

## 2021:A10 - Server Side Request Forgery (SSRF)

Points de contrôle:

* Validation stricte des URL fournies par les utilisateurs.
* Mise en place d'une liste blanche des destinations autorisées.
* Interdiction d'accéder aux adresses internes (localhost, réseau privé, métadonnées cloud, etc.).
* Limitation des protocoles autorisés (HTTP/HTTPS uniquement si nécessaire).
* Journalisation et surveillance des requêtes sortantes.

---

# 9. Pour aller un peu plus loin...

## 9.1 Encore une vulnérabilité

Vous avez résolu les challenges `/challenge1`, `/challenge2`, ..., `/challenge7`, mais êtes-vous certains qu'il n'en existe pas d'autres ?

Certaines applications Web utilisent directement des informations fournies par le client comme référence pour identifier la ressource à afficher. Si le serveur ne vérifie pas correctement les autorisations, un utilisateur peut accéder à des ressources qui ne lui sont pas destinées.

## 9.2 Une démonstration d'une vulnérabilité évoquée: CSRF

1. Rendez-vous sur: http://localhost:8080/demo1.
2. Choisissez un nom d'utilisateur unique afin de vous identifier.
3. Envoyez un message.
4. Cliquez sur le lien fourni par l'attaquant et observez attentivement l'adresse affichée: http://XXXXX.XXX/XXXX
5. Après quelques secondes, l'attaquant aura envoyé un message en votre nom.

## 9.3 Une petite erreur de code, exploitable avec l'architecture de production

Parfois, certaines applications sont vulnérables mais pas exploitables dans l'environnement de développement. Pourtant, dans l'environnement de production, elles sont bien vulnérables et exploitables. La différence entre le développement et la production vient de l'architecture. En production, on ajoute généralement différents composants pour sécuriser ou optimiser l'application, comme des WAF, des IPS/IDS, des systèmes de filtrage ou des reverse proxys. Ces composants peuvent interpréter, modifier ou mettre en cache les requêtes et les réponses, ce qui peut avoir des impacts inattendus sur la sécurité de l'application.

Vous pouvez exploiter une vulnérabilité dans le cache des pages 404 via la méthode GET, et une autre sur les pages 404 via la méthode POST. Pour obtenir le flag infectez les pages avec une balise script.

## 9.4 Est-ce possible sans cache ?

L'exercice 7 n'a pas cette "*mauvaise configuration*", pourtant une vulnérabilité devient exploitable sous le proxy qui tourne sur le port `tcp/8000`. L'exploitation est possible à cause de la présence du proxy, sans aucune mauvaise configuration, simplement parce que le serveur n'implémente pas certaines fonctionnalités.

> En résumé: le serveur seul contient une vulnérabilité non exploitable, avec le proxy devant le serveur la vulnérabilité devient exploitable alors qu'il n'y a aucune mauvaise configuration.

## 9.5 Race condition

**TODO**

## 9.6 Prototype pollution

**TODO**

## 9.7 CORS

**TODO** -> probablement à déplacer plus tôt dans le cours.

## 9.8 Supply chain attack

**TODO**

## 9.9 Mauvaises configurations

**TODO** -> Apache directory listing (.htaccess) -> faire un exercice.

## Conclusion

Il est important de vérifier le format des données fournies par l'utilisateur et de les encoder pour éviter les injections. Pour sécuriser une application, un grand nombre d'autres paramètres doivent être pris en compte.

Quelques exemples:

 - définir correctement les droits d'accès;
 - protéger les formulaires contre les requêtes non autorisées;
 - vérifier l'origine des requêtes.
 - **TODO**

---

# 10. Méthodologie des tests d'intrusion

**TODO**

---

# 11. Pratiquez !

Voici une application web vulnérable, serez capable de trouver les vulnérabilités et de les exploiter ?

---

# 12. Conclusion

La sécurité d'une application Web repose sur plusieurs principes fondamentaux:

* Ne jamais faire confiance aux entrées utilisateur.
* Séparer les données des instructions.
* Protéger les informations sensibles.
* Appliquer une authentification et des permissions robustes, en appliquant toujours un contrôle d'accès sur toutes les ressources, par défaut au plus restrictif.
* Maintenir les composants à jour.
* Concevoir la sécurité dès la conception, la sécurité et les approches du déploiement sont à prendre en compte.
* Auditer le code dans le même contexte qu'en production.
* Vérifier le code, par des revues humaines mais aussi par des outils d'analyse statique, dynamique, au runtime et automatiser la surveillance des vulnérabilités sur les composants prérequis. L'IA peut analyser du code pour les vulnérabilités.

# License

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).
