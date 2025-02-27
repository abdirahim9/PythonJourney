age= int(input("Enter your age: "))
if age >= 18:
    print("You're an adult! ")
    if age >= 21:
        print("You can drink legally too! ")
    else:
        print("No drinks yet-under 21! ")
else:
    print("You're a minor! ")
    if age < 13:
        print("You're a kid! ")
    else:
        print("You're a teen! ")
count = 0
while count < 5:
    print(f"Counting while: {count} ")
    count += 1
print(f"Finished counting to {count-1}-logic mastered! ")    