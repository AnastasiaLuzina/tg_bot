graph = {
     "7-6": "6",
     "7-3" : "9",
     "7-5" :"20",
     "6-7": "6",
     "6-3": "12",
     "6-4": "11", 
     "5-7": "20", 
     "5-2": "15", 
     "3-7": "9", 
     "3-2": "4", 
     "3-6": "12", 
     "4-6": "11",
     "4-2": "5",
     "4-1": "7",
     "2-1": "10",
     "2-4": "5",
     "2-3": "4",
     "2-5": "15",
     "1-2": "10",
     "1-4": "7"   
}
 
viewed = []
queue = []
start = "7"
distance =[10000,10000, 10000, 10000, 10000,10000, 0 ]
route = [1,2,3,4,5,6,7]


def neighbor(element):
    viewed.append(element)
    for neighbor in graph:
        if neighbor.startswith(f'element'):
            queue.append(neighbor)
            if neighbor not in viewed and neighbor not in queue :
                if distance[neighbor + 1] > graph[neighbor] + element:
                    distance[neighbor + 1].append(element)
                else:
                    distance[neighbor + 1].append(neighbor)
                        
                     
queue.append(start)

while queue:
    element = queue.pop(0)
    neighbor(element)
    
  
    




























""" graph = {
     "A": ["B", "F", "E", "C"],
     "B" : [],
     "E" : ["A", "D"],
     "F": ["A", "C"],
     "C": ["F", "A", "G"],
     "G": ["C", "H"],
     "D": ["E", "H"],
     "H": ["G", "I"]       
}
 
viewed = []
queue = []
start = "A"
search = "M"

def neighbor(element):
    viewed.append(element)
    for neighbor in graph[element]:
        if neighbor not in viewed and neighbor not in queue :
            queue.append(neighbor)
            
            
queue.append(start)

while queue:
    element = queue.pop(0)
    if element == search:
        print("Вершина найдена")
        break
    else:
        print("ВЕРШИНЫ НЕТ")
    neighbor(element)
    
     """
    
    
            
            
        
            

  