


def partition(array,low,high):


    pivot = array[high]

    i = low - 1 

    for j in range(low,high):

        if array[j] <=  pivot:

            i += 1 
            array[i],array[j] = array[j], array[i]

    array[i+1],array[high] = array[high], array[i+1] 

    return i + 1


def quicksort(array,low,high):

    # pivot = array[high]

    if len(array) == 1:
        return array 
    
    if low < high:

        p = partition(array,low,high)

        quicksort(array,low,p-1)
        quicksort(array,p+1,high )




if __name__ == '__main__':

    a = [2,321,31,321,1,45,1,2,68,9,1,0,-1]
    b = [4,13,51,5,6,9]

    quicksort(b,0,len(b)-1)

    print(b)