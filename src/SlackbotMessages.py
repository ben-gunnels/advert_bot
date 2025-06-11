class SlackBotMessages:
    VerboseConfirmation = "I will generate verbose update messages. Keeping you up to date on my task completion."
    ArchiveConfirmation = "I will try uploading the files in this channel to the folder in DropBox"
    Download = "Your submitted image has been downloaded..."
    PromptGenerated = "Seed prompt has been generated:"
    ImageGenerated = "Image has been generated..."
    ImageResized = "Image has been resized..."
    ImageSaved = "Image has been resized..."
    TrySending = "Image has been saved locally. I will try sending it in this channel..."
    AttemptingDropbox = "Image has been generated. I will try uploading to Dropbox..."
    DropboxSuccessful = "Image has successfully been uploaded to DropBox"

    # ERRORS
    PromptError = "There must be a flag and a body to this message to give the model direction. Try again using --inject followed by a prompt."
    SeriesError = "When using the --series flag you must specify one or more variable arguments. E.g. {1, 2, 3, 4} somewhere in your message. You must also only include a single image or prompt."
    DropboxError = "File could not be uploaded to DropBox"
    FilesNotShared = "You must share file(s) for an ad to be generated."
 
    def GeneratorError(e):
       return f"Something went wrong with ImageGeneratorBot :( Image request did not pass the vibe check. {e}"
    
    def DropboxUploadError(self, e):
       return f"There was an error uploading to Dropbox: {e}"

    def HelpMessage(self, user):
        return (f"Hello <@{user}>! :wave:\n\n"
                "To generate an AI image, please follow these steps:\n"
                "1. **Mention me** in your message (`@ImageGeneratorBot`).\n"
                "2. **Attach a valid image file** that I can use as a seed for your prompt.\n\n"
                "Some flags that you can add to your message to do exactly what you need:\n"
                "\t--verbose: Will give you feedback for most of the operations so that you know exactly what I'm doing\n"
                "\t--inject: Allows you to add a message to your prompt. Just type your message into the box following the flag.\n"
                "\t--series: Allows you to create a series of images from a single image or prompt\n"
                "I'll handle the rest and create your AI-generated image! :art:")

    def GeneratorConfirmation(self, filename):
        return f"Slack Bot will send a file with the name {filename} here... :hourglass_flowing_sand:"