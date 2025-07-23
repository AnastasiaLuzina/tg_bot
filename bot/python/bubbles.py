from termcolor import colored, cprint

array = [5,3,1,6,8,2,4]
print(array)

def print_array(first,second,array):
    print("[", end='')
    for i in range(len(array)):
        if array[i] == first:
            print(colored(first,'red'),end=',')            
        elif array[i] == second:
            print(colored(second,'red'), end=',')
        else:
            print(array[i], end=',')
    print("]")


for count in range(1, len(array)):
    flag = 0
    for i in range(len(array) - count):
        if array[i] > array[i+1]:  
            print("-------------------------------------")

            print("|")

            print_array(array[i],array[i + 1],array)

            first = array[i]
            array[i] = array[i + 1]
            array[i + 1] =  first
            print(colored(f"Поменяли элементы {array[i]} и {array[i+1]} местами", 'red'))

            print_array(array[i],array[i + 1],array)

            print("|")

            flag = 1

    if flag == 0:
        break
     
            
print(array)


