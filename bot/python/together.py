array = [1,6,0,3,2,8,4,9,7]

def split(array):  
    half = len(array)//2
    array_1 = array[:half] # 1,6,0,3
    array_2 = array[half:] # 2,8,4,9,7
    return array_1, array_2


#левая включается в срез правая не включается

def sorted(array):
    if len(array) <= 1:
        return array
    
    else:
        left, right = split(array)
        left = sorted(left)
        right = sorted(right)
        return join(left,right)
        

def join(array_1,array_2):
    result =[]
    index_1 = 0
    index_2 = 0
    for i in range(len(array_1) + len(array_2)):

        if index_1 == len(array_1):
            for i in range(index_2, len(array_2)):
                result.append(array_2[i])
            break

        elif index_2 == len(array_2):
            for i in range(index_1, len(array_1)):
                result.append(array_1[i])
            break 

        elif array_1[index_1] <= array_2[index_2]:
            result.append(array_1[index_1])
            index_1 += 1

        elif array_1[index_1] > array_2[index_2]:
            result.append(array_2[index_2])
            index_2 += 1
        
    return result
       


print(sorted(array))

