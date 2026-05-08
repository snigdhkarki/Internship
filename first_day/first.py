try:
    marks = float(input("Enter the student's marks: "))

    if marks >= 90:
        print("Grade: A")
    elif marks >= 80:
        print("Grade: B")
    elif marks >= 70:
        print("Grade: C")
    elif marks >= 60:
        print("Grade: D")
    else:
        print("Grade: Fail")
except ValueError:
    print("Invalid input! Please enter a numerical value.")