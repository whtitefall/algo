

def mergesort(array):

    if len(array) > 1 :
        # print(1)
        mid = len(array) // 2 

        # print(array)
        l = array[:mid]
        # print(l)
        r = array[mid:]
        # print(array,mid,l,r)
        mergesort(l)
        mergesort(r)
        merge(array, l, r)

def merge(array,l,r,):

    i,j,k = 0,0,0  

    while i < len(l)  and  j < len(r) :
        # print(i,j)
        if l[i] <  r[j]:
            array[k] = l[i]
            i +=1 
        else :
            array[k] = r[j]
            j+=1 

        k += 1 


    while i < len(l) or j < len(r):

        if i < len(l):
            array[k] = l[i]
            i += 1 

        elif j < len(r):
            array[k] = r[j]
            j += 1 
        k += 1 
        



        


if __name__ == '__main__':

    a = [2,321,31,321,1,45,1,2,68,9,1,0,-1]

    mergesort(a)

    print(a)