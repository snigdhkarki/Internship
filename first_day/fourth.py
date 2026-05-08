def count_words_in_file(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()
            words = content.split()
            print(f"Total number of words in '{filename}': {len(words)}")
            
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found. Please check the path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

count_words_in_file("sample.txt")