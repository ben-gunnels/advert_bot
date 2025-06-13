__all__ = ["generate_prompt"]

def generate_prompt(injection=""):
    dense_prompt = """
        Add the design to the model wearing a blank T-Shirt. Ensure that the design is well fitted for the shirt and that the image
        can be used to advertise the design of the image. Keep the design moderately sized on the shirt.
    """

    dense_prompt += injection

    return dense_prompt
