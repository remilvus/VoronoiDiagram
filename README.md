#Dokumentacja
Algorytm wyznaczania Wieloboków Voronoi 
dla metryki nieuklidesowskiej wraz z wizualizacją

#Wykorzystany Algorym
Do rozwiązania zagadnienia użyliśmy Algorytmu Fortuny

#Złożoność obliczeniowa algorytmu
O(n*logn)


#Wykorzystana metryka

#Metryka maximum
	d(x,y)=max(|x1-x2|,|y1-y2|)







#Struktury

PriorityQueue:
    klucz: 
    dane: x, y, typ punktu (poczakowy/środkowy/zgięcie/granica), valid,
          odcinki do dodania, odpowiadające punktowi środki komórek
    
RBTree:
    klucz: wsp. x środka komórki
    dane: eventy związane z punktem
    
VoronoiDiagram:
    collection of line segments
	

#Podfunkcje geometryczne
	Wyznaczanie symetralnej:
		bisector(A, B, rangex=[0,1],rangeY[0,1])
	Znajdowanie przecięcia symetralnych:
		findCross(line1, line2)
	Znajdowanie przecięcia linii:
		line_intersection

#Klasa Voronoi
	Zawiera:
		PriorityQueue przechowujące eventy
		RBTree trzyma aktywne początkowe punkty
		Lista zachowująca linie dołączone do diagramu Voronoi
			output
		Inne listy i zmienne w celach technicznych 
			opisane komentarzami z poziomu kodu		
	
