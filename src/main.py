import logging
import subprocess
import json

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

process_history = [0, 0, 0]

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    pass


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Work in progress")

async def gpustatus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get the GPU status
    nvidia_smi_output = subprocess.check_output(["nvidia-smi", "--query-gpu=utilization.gpu,memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"])
    # Get the processes running on the GPU
    nvidia_smi_processes = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"])
    processes = nvidia_smi_processes.decode("UTF-8")
    processes = processes.split("\n")
    # Loop over the process and split them by ,
    for i in range(len(processes)):
        processes[i] = processes[i].split(",")
    # Remove the last element of the list
    processes.pop()
    # Loop through the processes and get the usernames
    usernames = []
    for process in processes:
        username = subprocess.check_output(["ps", "-o", "user=", "-p", process[0]])
        usernames.append(username.decode("UTF-8"))
        # Remove newlines from the username
        usernames[-1] = usernames[-1].replace("\n", "")
    gpu_status = nvidia_smi_output.decode("UTF-8")
    # Split the output into a list divided by ,
    gpu_status = gpu_status.split(",")
    # Format the output
    message = f"Total Memory: {int(gpu_status[1])}MB\nUsed Memory: {int(gpu_status[2])}MB\nFree Memory: {int(gpu_status[3])}MB\n"
    if len(processes) != 0:
        message = message + "\nUsers:\n"
        for i in range(len(processes)):
            # Remove spaces from the username and the memory usage
            processes[i][1] = processes[i][1].replace(" ", "")
            gpu_user = f"User: {usernames[i]} -> {processes[i][1]}MB\n"
            message = message + gpu_user
        message = message + "\n"
    if len(processes) != 0:
        message = message + "WARNING: GPU is being used"
    else:
        message = message + "GPU is not being used"
    await update.message.reply_text(message)
    
async def periodic_gpustatus(context: ContextTypes.DEFAULT_TYPE):
    # Get the GPU status
    nvidia_smi_output = subprocess.check_output(["nvidia-smi", "--query-gpu=utilization.gpu,memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"])
    # Get the processes running on the GPU
    nvidia_smi_processes = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"])
    processes = nvidia_smi_processes.decode("UTF-8")
    processes = processes.split("\n")
    # Loop over the process and split them by ,
    for i in range(len(processes)):
        processes[i] = processes[i].split(",")
    # Remove the last element of the list
    processes.pop()
    # Loop through the processes and get the usernames
    usernames = []
    for process in processes:
        username = subprocess.check_output(["ps", "-o", "user=", "-p", process[0]])
        usernames.append(username.decode("UTF-8"))
        # Remove newlines from the username
        usernames[-1] = usernames[-1].replace("\n", "")
    gpu_status = nvidia_smi_output.decode("UTF-8")
    # Split the output into a list divided by ,
    gpu_status = gpu_status.split(",")
    # Format the output
    message = f"Total Memory: {int(gpu_status[1])}MB\nUsed Memory: {int(gpu_status[2])}MB\nFree Memory: {int(gpu_status[3])}MB\n"
    if len(processes) != 0:
        for i in range(len(processes)):
            message = message + "\nUsers:\n"
            # Remove spaces from the username and the memory usage
            processes[i][1] = processes[i][1].replace(" ", "")
            gpu_user = f"User: {usernames[i]} -> {processes[i][1]}MB\n"
            message = message + gpu_user
        message = message + "\n"
    # Check if the GPU is now beiung used
    print_message = False
    if (process_history[0] != 0) and (process_history[1] == 0) and (len(processes) != 0):
        message = message + "GPU is now being used\n"
        print_message = True
    if (process_history[0] == 0) and (process_history[1] != 0) and (len(processes) == 0):
        message = message + "GPU is no longer being used\n"
        print_message = True
    print(process_history)
    process_history[2] = process_history[1]
    process_history[1] = process_history[0]
    process_history[0] = len(processes)
    # if float(gpu_status[2]) > float(gpu_status[1])/10:
    #     message = message + "WARNING: GPU is being used"
    # else:
    #     message = message + "GPU is not being used"
    if print_message:
        with open("../conf.json") as json_file:
            data = json.load(json_file)
            group_id = data["group_id"]
            await context.bot.send_message(chat_id=group_id, text=message)
    
    
def is_gpu_used():
    nvidia_smi_output = subprocess.check_output(["nvidia-smi", "--query-gpu=utilization.gpu,memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"])
    # Get the processes running on the GPU
    nvidia_smi_processes = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"])
    processes = nvidia_smi_processes.decode("UTF-8")
    processes = processes.split(",")
    
    # Get the username of the user running the process
    username = subprocess.check_output(["ps", "-o", "user=", "-p", processes[0]])
    gpu_status = nvidia_smi_output.decode("UTF-8")
    # Split the output into a list divided by ,
    gpu_status = gpu_status.split(",")
    if float(gpu_status[2]) > float(gpu_status[1])/10:
        return True
    else:
        return False
    
    
def main() -> None:
    """Start the bot."""
    # Read the token from the conf.json file
    with open("../conf.json") as json_file:
        data = json.load(json_file)
        token = data["api_key"]
        group_id = data["group_id"]
        
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token=token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("gpustatus", gpustatus))
    
    job_queue = application.job_queue
    # Add a periodic function to check the GPU status
    periodic_task = job_queue.run_repeating(periodic_gpustatus, interval=600, first=0) 

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()