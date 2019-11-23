# VoronoiDiagram


# metryka maximum <br>
  	max(|x1-x2|,|y1-y2|) 
  	wyznaczanie symetralnej 
# inne kwestie geometryczne <br>
  	wyznaczanie prostej(?)  
  	przecięcia linii 
	
#Algorytm Fortuny:
	Definiujemy granice
	
	Legenda:
		Punkt początkowy - środki wielokątów
		Punkt środkowy - punkt przecięcia symetralnych
	Główna pętla:
		Zabieramy event z PriorityQueue
		Jeśli punkt poczatkowy:
			dodajemy do miotły
			obliczamy punkt(punkty???) przecięcia z sąsiadami
			Oznaczamy jako do dodania i dodajemy do priorityQueue
				z kluczem  najniższego położenia y należącego 
				do jego kwardratu ("okręgu")
			Punkty które nie powstaną oznaczamy jako do wywalenia
		Jeśli punkt środkowy:
			Dodajemy punkt do diagramu
		
