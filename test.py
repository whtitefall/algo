def qs(arr):
    print(arr and (qs([i for i in arr[1:] if i< arr[0]])) + \
         [arr[0]] + \
         (qs([i for i in arr[1:] if i >= arr[0]])))

    return arr and (qs([i for i in arr[1:] if i< arr[0]])) + \
         [arr[0]] + \
         (qs([i for i in arr[1:] if i >= arr[0]]))



# print(qs([1,2,41,2,9,12]))
a = []
print(a[2:])