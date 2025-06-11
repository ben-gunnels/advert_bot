from generate_image import *

def main():
    test_attributes = [
        ("female", "white"),
        ("male", "blue"),
        ("female", ""),
        ("", "red"),
        ("", "")
    ]

    for i, a in enumerate(test_attributes):
        print(f"Test case: {i}")
        print(f"Attributes: {a}")
        model = select_model(a)
        print(model)
        print("-"*20)

if __name__ == "__main__":
    main()