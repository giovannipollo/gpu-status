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
    processes = processes.split(",")
    
    # Get the username of the user running the process
    username = subprocess.check_output(["ps", "-o", "user=", "-p", processes[0]])
    gpu_status = nvidia_smi_output.decode("UTF-8")
    # Split the output into a list divided by ,
    gpu_status = gpu_status.split(",")
    # Format the output
    message = f"Total Memory: {int(gpu_status[1])}MB\nUsed Memory: {int(gpu_status[2])}MB\nFree Memory: {int(gpu_status[3])}MB\n"
    gpu_user = f"User: {username.decode('UTF-8')}\n"
    message = message + gpu_user
    if float(gpu_status[2]) > float(gpu_status[1])/10:
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
    processes = processes.split(",")
    
    # Get the username of the user running the process
    username = subprocess.check_output(["ps", "-o", "user=", "-p", processes[0]])
    gpu_status = nvidia_smi_output.decode("UTF-8")
    # Split the output into a list divided by ,
    gpu_status = gpu_status.split(",")
    # Format the output
    message = f"Total Memory: {int(gpu_status[1])}MB\nUsed Memory: {int(gpu_status[2])}MB\nFree Memory: {int(gpu_status[3])}MB\n"
    gpu_user = f"User: {username.decode('UTF-8')}\n"
    message = message + gpu_user
    if float(gpu_status[2]) > float(gpu_status[1])/10:
        message = message + "WARNING: GPU is being used"
    else:
        message = message + "GPU is not being used"
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
    
# async def periodic_gpu_check(context: ContextTypes.DEFAULT_TYPE):
#     # Get the GPU status
#     current_gpu_status = is_gpu_used()
#     if current_gpu_status == True and gpu_status[1] == False and gpu_status[2] == False:
#         awaits = await gpustatus(context)
#         temp = gpu_status[0]
#         gpu_status[0] = current_gpu_status
#         gpu_status[2] = gpu_status[1]
#         gpu_status[1] = temp
#     elif current_gpu_status == False and gpu_status[1] == True and gpu_status[2] == True:
#         awaits = await gpustatus(context)
#         temp = gpu_status[0]
#         gpu_status[0] = current_gpu_status
#         gpu_status[2] = gpu_status[1]
#         gpu_status[1] = temp    
    
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
    periodic_task = job_queue.run_repeating(periodic_gpustatus, interval=10, first=0) 

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()