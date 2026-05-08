def find_largest(numbers):
    if not numbers:
        return "The list is empty."
    
    largest = numbers[0]
    
    for num in numbers:
        if num > largest:
            largest = num
            
    return largest

my_list = [15, 42, 7, 89, 23, 56]
print(f"The largest number in the list is: {find_largest(my_list)}")