import os

def count_subdirectories(directory):
    """
    Returns the number of subdirectories in the given directory.

    Parameters:
    directory (str): The path to the directory.

    Returns:
    int: The number of subdirectories.
    """
    try:
        return sum(os.path.isdir(os.path.join(directory, entry)) for entry in os.listdir(directory))
    except FileNotFoundError:
        print(f"The directory {directory} does not exist.")
        return 0
    except PermissionError:
        print(f"Permission denied to access the directory {directory}.")
        return 0