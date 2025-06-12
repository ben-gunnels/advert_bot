import os
import random
import datetime
from slack_helper import *
from generate_prompt import *
from generate_image import *
from utils import *
from vars import *
from SlackbotMessages import SlackBotMessages
from reformat_image import resize_image
from dropbox_helper import *

messages = SlackBotMessages()

EVENTS = {
    "message",
    "app_mention",
    "file_shared"
}

VALID_FLAGS = {
    "verbose",
    "help",
    "inject",
    "attributes"
}

MODELS_FOLDER_ID = os.getenv("MODELS_FOLDER_ID")

valid_channels = set(CHANNEL_MAP.keys())

class EventHandler:
    model_path = "./models/model.png"

    def __init__(self, logger, event_type: str, channel_id: str, user: str, text: str, files: list):
        if channel_id not in valid_channels:
            return 
        
        if event_type not in EVENTS:
            return 
        
        self.event_type = event_type # app_mention, file_shared, message, etc.
        self.channel_id = channel_id
        self.input_filename = None

        self.dropbox_folder_id = CHANNEL_MAP[channel_id]
        
        self.user = user # The Slack User ID of the message sender
        self.text = text # The text body of the slack message
        self.files = files # Files embedded in the slack message
        self.logger = logger # Common logging object

        # Flags passed by user
        self.verbose = False # Gives step by step feedback of the generation process
        self.help = False # User invokes help instructions from the bot
        self.inject = False # Allows the user to add text to the image generation prompt directly
        self.attributes = False # Whether a model is specified for the design.

        self.attribute_params = ()

        try:
            # Save memory by removing any existing folder structures from the app
            remove_directory_recursively("user_submitted_files")
            remove_directory_recursively("image_outputs")
            remove_directory_recursively("models")
        except:
            pass

        self._mkdirs("user_submitted_files")
        self._mkdirs("image_outputs")
        self._mkdirs("models")

        self._set_flags()

    def handle_event(self):
        """
            Delegates the handling of the message to the specified function. 
        """
        if self.event_type == "app_mention":
            self.logger.info("Handling app_mention...")
            self._handle_app_mention()
        elif self.event_type == "file_shared":
            self.logger.info("Handling file shared...")
            self._handle_files_shared()    

    def _handle_app_mention(self):
        """
            Main entry when the bot is mentioned in the message. 
            It facilitates the functionality that the user is seeking.
            Sends a help message if the user solicits help.
            Initiates the process for file download and image generation.
            If no file is submitted it invokes the direct prompt image generator.
        """
        if self.help: # If the help flag is present
            message = messages.HelpMessage(self.user)
            send_message(self.channel_id, message)

        if self.attributes:
            self.attribute_params = get_attributes(self.text)
            print(self.attribute_params)

        if self.files: # The user has submitted a file to be edited
            self._handle_files_shared()
        else: # The user has not submitted a file to be edited
            send_message(self.channel_id, messages.FilesNotShared)

    def _handle_files_shared(self):
        """
            Sends each file in the batch off to be handled by the file handler.
            Treats a batch continuously.
        """
        for file in self.files:
            self._handle_file_shared(file)
        return

    def _handle_file_shared(self, file):
        """
            This process downloads the file from slack through the channel.
            It then uploads the image along with the prompt to the OpenAI image generation API.
            The file is then sent through the slack channel. 
        """
        if file:
            ext = file.get("filetype").lower()
        else:
            ext = "png"
        
        self._get_file_from_user(file, ext)
        self._facilitate_output(self.input_filename.split('/')[-1][:-4])

    def _facilitate_output(self, input_filename):
        """
            Handles the naming of the output file, sending confirmation messages.
            Calls the generate image and send function. 
        """
        # Unconditionally set the extension to png if it is being generated
        output_filename = f"image_outputs/gen_image_{input_filename}.png" 
        send_message(self.channel_id, messages.GeneratorConfirmation(output_filename.split('/')[-1]))

        if self.verbose:
            send_message(self.channel_id, messages.VerboseConfirmation)

        self._generate_image_and_send(output_filename)

    def _get_file_from_user(self, file, ext):
        """
            Function handles trying to download the file that a user attached to the message.
            As a side effect it generates the input filename for use later. 
        """
        # Name the file that will be saved from the User's message
        now = datetime.datetime.now()
        self.input_filename = f"user_submitted_files/{now.strftime('%Y-%m-%d-%H-%M-%S')}.{ext}"

        # From slack helper
        download_slack_file(file["url_private"], self.input_filename)
        if self.verbose:
            send_message(self.channel_id, messages.Download)
     
    def _handle_image_prompt_and_generation(self, output_filename):
        """"
            Generates the image prompt and the generation of an Ai generated image.
            It handles the cases of prompt-only and image-edit.
                prompt-only: No image has been uploaded to the message. The generator will use the client.image.create method to
                    try to create an an image based on the text body given by the sender.
                image-edit: An image has been uploaded to the message. The generator will use the client.image.edit method
                    to try to edit the given image and return a suitable design.
        """
        try:
            generated_prompt = self._generate_prompt()
            generated_image = self._generate_image(generated_prompt)

            # Reformat the image to proper dimensions and specs
            generated_image = resize_image(generated_image)
            
            self.logger.info("Image Resized")
            if self.verbose:
                send_message(self.channel_id, messages.ImageResized)

            generated_image.save(output_filename)
            if self.verbose:
                send_message(self.channel_id, messages.TrySending)
            self.logger.info(f"Generated image saved to {output_filename}")

            return 200
        
        except Exception as e:
            send_message(self.channel_id, messages.GeneratorError(e))
            print(f"Image generation could not be completed. {e}")

    def _generate_prompt(self):
        """
            Create the prompt needed to generate the image. 
            Handles the case where a vanilla prompt is entered and when an Image is being edited. 
        
        """
        if self.inject:
            # Inject the clean text into the prompt to help add instructions.
            text = clean_text(self.text)

        # Just return the boilerplate prompt
        if self.inject:
            generated_prompt = generate_prompt() + text
        else:
            print("generating prompt...")
            generated_prompt = generate_prompt()

        self.logger.info("Prompt generated")
        if self.verbose:
            send_message(self.channel_id, messages.PromptGenerated)
            send_message(self.channel_id, generated_prompt)
        
        return generated_prompt
    
    def _select_model(self, attributes: tuple):
        # sex, color
        s, c = attributes

        # Start building the model path
        if not s:
            s = random.choice(["female", "male"])

        if not c:
            c = random.choice(["white", "black", "red", "blue"])
        
        model_path = f"/{s}/{c}/"

        number_suitable_files = count_files_in_subfolder(MODELS_FOLDER_ID, model_path)['file_count']
        endfile = f"{random.randrange(1, number_suitable_files+1)}.png" # Get the endfile path, all files are numbered

        res = download_file_from_shared_folder(MODELS_FOLDER_ID, model_path+endfile, self.model_path)
        print(f"Downloading Model from Dropbox: {res}")
    
    def _generate_image(self, generated_prompt):
        """
            Makes the call to generate the image. 
        """
        if self.attributes:
            ordered_attributes = ["", ""]
            for a in self.attribute_params:
                if a in MODEL_ATTRIBUTES["sex"]:
                    ordered_attributes[0] = a
                elif a in MODEL_ATTRIBUTES["shirt-color"]:
                    ordered_attributes[1] = a
            ordered_attributes = tuple(ordered_attributes) # Ordered attributes should be (sex, shirt-color)

        # Generate the model file
        self._select_model(ordered_attributes)

        # Make a call to OpenAi image generation model based on the prompt
        generated_image = edit_image(generated_prompt, self.input_filename, self.model_path)

        if self.verbose: 
            send_message(self.channel_id, messages.ImageGenerated)
        
        return generated_image
    
    def _generate_image_and_send(self, output_filename):
        """
            Handles the end stage of the image generation process. It makes a call to the image prompter and generator.
            Handles the resizing and sends the message. 
            This function acts as an intermediary between the caller and the _handle_image_prompt_and_generation function.
        """
        if self._handle_image_prompt_and_generation(output_filename) == 200:
            # Send the output to dropbox
            send_message(self.channel_id, messages.AttemptingDropbox)

            try:
                response = upload_to_shared_folder(output_filename, self.dropbox_folder_id)
                if response.get("error"):
                    send_message(self.channel_id, messages.DropboxUploadError(response))
                else:
                    send_message(self.channel_id, messages.DropboxSuccessful)
            except Exception as e:
                print(f"Dropbox file upload failed: {e}")

            send_file(self.channel_id, output_filename)
            self._cleanup(output_filename)

    def _mkdirs(self, folder_path):
        """
            Initializes the necessary folders used for image saving and generation.
        """
        # Check if the folder exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            self.logger.info(f"Created directory: {folder_path}")
        else:
            self.logger.info(f"Directory already exists: {folder_path}")

    def _set_flags(self):
        """
            Initializes the flag properties for the object. 
            Finds the flags in the message which are prepended by --.
        """
        self.flags = find_flags(self.text)

        for flag in VALID_FLAGS:
            if flag in self.flags:
                setattr(self, flag, True) 

    def _cleanup(self, output_filename):
        """
            Removes the images that have been saved locally and temporarily.
            Removes the input image files and the generated output files.
        """
        # Remove stored slack image
        if self.input_filename and os.path.exists(self.input_filename):
            os.remove(self.input_filename)
   
        if output_filename and os.path.exists(output_filename):
            os.remove(output_filename)



