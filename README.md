# README

## Funktionen

### Menüleiste

In der Menüleiste gibt es einige Funktionen:

File: Wechseln zwischen Dark-/ und Lightmode, Beenden des Programms

Navigieren: Ändern der aktuellen Programmseite. (Gleiche Funktion wie die darunterliegende Navigationsleisten)

Hilfe: Über-Seite, Dokumentation (öffnen dieser README.md), Support (öffnet Seite zum Melden von Problemen über E-Mail oder GitHub), Updates überprüfen (Prüft nach neuen Updates, falls vorhanden kann dieses direkt heruntergeladen werden; aktuell entsteht dabei noch eine
Fehlermeldung, diese kann allerdings ignoriert werden.)

### Es gibt 4 verschiedene Funktionen
### Gruppen

Fügt Gruppen zu der Datenbank hinzu. Beachtet, dass die Gruppennummern der Reihenfolge des Hinzufügens in die Datenbank entspricht. Wenn ihr eine Gruppe löscht, wird die ID (Gruppennummer) nicht automatisch wiederverwendet (Bsp.: 1,2,3,4,5 -> 2 wird gelöscht und neue 
Gruppe hinzugefügt -> 1,3,4,5,6). Um das zu umgehen editiert stattdessen die Gruppennamen oder löscht die darauffolgenden Nummern (Bsp.: 1,2,3,4,5 -> 3 wird gelöscht -> 4,5 wird gelöscht und neue hinzugefügt -> 1,2,3,4).

### Schüler

Fügt Schüler zu der Datenbank hinzu. Fügt Namen immer im selben Format hinzu (Vor Nach/ Nach, Vor) um euch die Sortierung zu erleichtern. Schreibt die Klasse **IMMER!** im selben Format an (bspw. 5/4) OHNE irgendwo ein anderes Zeichen hinzuzufügen (Leerzeichen vor/nach
Klasse), sonst funktioniert die Funktion min./max. Schüler pro Klasse nicht korrekt. Gebt Erst-/Zweit-/Drittwunsch als Nummern an, nicht als Name!

### GENERIEREN 

Generiert die best mathematisch gesehene Zuteilung in der Zuteilungstabelle. Gebt bei den Limits eure jeweiligen Limits an. Wenn es keine Limits geben soll, gebt einfach bei max. 100 und bei min. 1 ein.

### BEARBEITEN

Hier könnt Ihr die Datenbanken ansehen/bearbeiten. Die "ID" Parts können nicht bearbeitet werden, da diese die Primärschlüssel der Datenbanken sind. Die Zuweisungstabelle kann zusätzlich auch nicht bearbeitet werden, Änderungen aus der Schüler-/Gruppenliste wird 
allerdings automatisch übernommen. Um die Tabellen nach Bearbeitungen zu aktualisieren kann der "Reload" Button verwendet werden. Um die Zuweisungen selber zu ändern ist es also notwendig sie manuell in einer PDF/CSV Datei zu ändern. Zum Sortieren drückt auf die
Kategorie, die sortiert werden soll. Beim Exportieren wird die aktuelle Sortierung verwendet. Um die exportierte CSV in Excel zu öffnen, folgt gerne dieser Anleitung: https://www.hesa.ac.uk/support/user-guides/import-csv. Es können theoretisch auch Online-Converter
verwendet werden, beachtet dabei, dass dabei die Datenbank mit Daten an den Anbieter und eventuell auch an Dritte weitergegeben werden.

## ANDERES

### INSTALLATION & UPDATE

Für die erstmalige Installation ladet sowohl die .exe und die .db herunter und schiebt beide in den selben Ordner (egal wo). Für Updates (und um die aktuelle Datenbank zu behalten) kann sowohl die integrierte Updatefunktion benutzt werden oder es wird die alte .exe
gelöscht und die neue hier direkt aus GitHub installiert.

### COPYRIGHT

Dieses Projekt ist für das 11er Projekt des Romain-Roland-Gymnasium Dresden gebaut. Für andersweitige Nutzung, Verteilung oder Bearbeitung/Weiterverwendung des Codes kontaktiert mich über GitHub.

### DATENSCHUTZ

Alle Namen, Klassen, Gruppen und Zuordnungen werden lokal in der gruppenzuweisungen.db Datenbank gespeichert. Keine Daten werden auf Server oder anderes hochgeladen bzw. gespeichert. Es wird außschließlich beim Aktualisieren der Software eine Verbindung zum Internet
benötigt um die neuen Dateien von GitHub zu downloaden.
