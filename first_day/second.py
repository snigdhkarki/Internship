try:
    num = int(input("Enter a number to see its multiplication table: "))

    print(f"\nMultiplication Table for {num}:")
    for i in range(1, 11):
        print(f"{num} x {i} = {num * i}")
except ValueError:
    print("Please enter a valid integer.")