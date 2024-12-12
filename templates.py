import os
import subprocess
import ollama
from dotenv import load_dotenv


# Load .env file
load_dotenv('./env')

# Access variables directly from environment
temperature = float(os.getenv('TEMPERATURE'))
num_ctx = int(os.getenv('NUM_CTX'))
num_predict = int(os.getenv('NUM_PREDICT'))
test_cpu = int(os.getenv('TEST_CPU'))

system_message_l = ["You are an advanced language model specialized in text summarization. Your task is to process transcribed audio and produce extensive and comprehensive summaries. Follow these guidelines:",
"1. **Context Preservation:** Accurately capture the key points, nuances, and tone of the original content. Maintain the original intent and message of the speaker(s).",
"2. **Clarity and Coherence:** Write the summary in a clear, structured, and logical format, ensuring it flows naturally and is easy to understand.",
"3. **Extensiveness:** Provide a detailed summary that includes all significant aspects of the transcript, such as arguments, examples, and conclusions. Aim to create a thorough representation rather than a brief overview.",
"4. **Segmentation:** If the video covers multiple topics, organize the summary into distinct sections or headings reflecting those topics.",
"5. **Focus on Relevance:** Exclude irrelevant information, filler words, and repetitive content unless they contribute meaningfully to the context.",
"6. **Formatting:** Adhere strictly to the markdown format. Use line breaks, title and subtitle headings, bullet points, numbered lists, or subheadings as appropriate to enhance readability and comprehension.",
"7. **Neutrality:** Remain objective and avoid introducing any bias or personal interpretations.",
"Produce a well-rounded and exhaustive summary that provides the reader with a deep understanding of the video content without the need to refer to the original transcript."]

def gen_string(line_list): 
    out_string = ""
    for n in line_list:
        out_string = ("\n".join(str(n) for n in line_list) + "\n")
    return out_string

def read_gemini_sysmsg():
    gemini_message_l = []
    with open("./gemini_instructions", "r") as f:
        gemini_message_l = []
        lines = f.readlines()
        for line in lines:   
            read_line = line
            gemini_message_l.append(read_line)
        return gemini_message_l
        

def generate_modelfile(model_name, model_family):
    if not os.path.isdir("./modelfiles"):
        os.makedirs("./modelfiles")        
    model_file = f"./modelfiles/Modelfile-{model_family}"
    if os.path.isfile(model_file):
        os.remove(model_file)       
    with open(model_file,mode = "a") as Modelfile:
        Modelfile.write("FROM "+str(f"{model_name}")+ "\n")
        Modelfile.write("PARAMETER temperature "+ str(temperature)+ "\n")
        Modelfile.write("PARAMETER num_ctx "+str(num_ctx)+ "\n")
        Modelfile.write("PARAMETER num_predict "+str(num_predict)+ "\n")
        Modelfile.write('SYSTEM """'+"\n")
        Modelfile.write(sys_message)
        Modelfile.write('"""')
    print("Created modelfile for "+model_name)

def create_model_from_file(model_name,model_family):
    model_file = str(f"./modelfiles/Modelfile-{model_family}")
    with open("./models.txt", "r") as txt_models:
        subprocess.Popen(['ollama', 'create', f"{model_name}-summarizer", '-f', f"{model_file}"],stdout=None, stderr=None)
        print("Added model "+f"{model_name}-summarizer"+" to ollama!")

def gen_ollama_models():
    """
    Retrieve and print the list of available Ollama models.
    """
    try:
        # Fetch the list of local models
        models = ollama.list()
        for model in models['models']:
            model_n = str(f"{model['model']}")
            model_f = str(f"{model['details'].family}")
            generate_modelfile(model_n, model_f)
            pattern = "-summarizer"
            if pattern not in model_n:
             create_model_from_file(model_n, model_f)

    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    #model_list = ollama.models()
    #for model_n in model_list:
   #     generate_modelfile(model_n)
    #    create_model_from_file(model_n)

    sys_message = gen_string(system_message_l)
    os.environ["SYSTEM_MESSAGE"] = sys_message
    if os.path.isfile("./models.txt"):
        os.remove("./models.txt")
    models = ollama.list()
    with open("./models.txt", "a") as models_txt:
        for model in models['models']:
            model_n = str(f"{model['model']}")
            model_f = str(f"{model['details'].family}")      
            models_txt.write(model_n+"\n")
        models_txt.write('gemini'+"\n")        
    gen_ollama_models()