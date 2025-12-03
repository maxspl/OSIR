

def singleton(cls):
    """
    Decorator to transform a class into a singleton. Ensures that only one instance of the class exists within the application.

    Args:
        cls (type): The class to be transformed into a singleton.

    Returns:
        function: A wrapper function that manages the instantiation of the singleton class, ensuring only one instance is created.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        """
        Retrieves or creates an instance of the class. This function checks if an instance already exists;
        if not, it creates a new one using provided arguments.

        Args:
            *args: Variable length argument list for class instantiation.
            **kwargs: Arbitrary keyword arguments for class instantiation.

        Returns:
            object: The singleton instance of the class.
        """
        nonlocal instances
        # print(instances, id(instances))
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
