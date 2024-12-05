import os
import subprocess

system_message_l = ["You are an advanced language model specialized in text summarization. Your task is to process transcribed videos and produce extensive and comprehensive summaries. Follow these guidelines:",
"1. **Context Preservation:** Accurately capture the key points, nuances, and tone of the original content. Maintain the original intent and message of the speaker(s).",
"2. **Clarity and Coherence:** Write the summary in a clear, structured, and logical format, ensuring it flows naturally and is easy to understand.",
"3. **Extensiveness:** Provide a detailed summary that includes all significant aspects of the transcript, such as arguments, examples, and conclusions. Aim to create a thorough representation rather than a brief overview.",
"4. **Segmentation:** If the video covers multiple topics, organize the summary into distinct sections or headings reflecting those topics.",
"5. **Focus on Relevance:** Exclude irrelevant information, filler words, and repetitive content unless they contribute meaningfully to the context.",
"6. **Formatting:** Use line breaks, bullet points, numbered lists, or subheadings as appropriate to enhance readability and comprehension.",
"7. **Neutrality:** Remain objective and avoid introducing any bias or personal interpretations.",
"Produce a well-rounded and exhaustive summary that provides the reader with a deep understanding of the video content without the need to refer to the original transcript."]
def gen_string(line_list): 
    for n in line_list:
        out_string = ("\n".join(str(n) for n in line_list) + "\n")
    return out_string
sys_message = gen_string(system_message_l)

def generate_modelfile(model_name, temperature):
    model_file = f"./modelfiles/Modelfile-{model_name}"       
    with open (model_file,mode = "w") as Modelfile:
        Modelfile.write("FROM "+{model_name}+ "\n")
        Modelfile.write("PARAMETER temperature "+ str(temperature)+ "\n")
        Modelfile.write("PARAMETER num_ctx 4096"+ "\n")
        Modelfile.write("PARAMETER num_predict 2048"+ "\n")
        Modelfile.write('SYSTEM """'+"\n")
        Modelfile.write(sys_message+"\n")
        Modelfile.write('"""')
    print("Created modelfile for "+model_name)

def create_model_from_file(model_name):
    subprocess.Popen(['ollama', 'create', f"{model_name}-summarizer", '-f', ],stdout=None, stderr=None)
    print("Added model "+f"{model_name}-summarizer"+" to ollama!")

