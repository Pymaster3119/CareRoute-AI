import DataStorage.datastorage
import AIScripts.runVLM
import AIScripts.runLLM
def add_user(username, email, password, location):
    result = DataStorage.datastorage.add_user(username, email, password, location)
    if not result:
        return f"User {username} already exists!"
    return f"User {username} added successfully!"

def add_doctor(name, password, specialty, email, workplace, degree_dir):
    #Degree scanning
    legitimacy = AIScripts.runVLM.run_vlm("You are an expert at analysing people's degrees", "Can you tell me if this prompt is legitimate? If it is illegitimate, output \"illegitimate\" as your final output. If it is legitimate, output \"legitimate\" as your final output. Do not output any other strings.", degree_dir)
    if "illegitimate" in legitimacy.lower():
        return "Degree deemed invalid"
    degree = AIScripts.runVLM.run_vlm("You are an expert at analysing people's degrees", "Please output a short description of the degree pictured and the skills expected from a person with this degree.", degree_dir)

    #Get the summary and save it
    summary = AIScripts.runLLM.run_llm(f"You are an expert at writing doctor summaries. Write a short summary of the skills a doctor with the following specialty: {specialty}, workplace: {workplace}, and degree: {degree} will have. The summary should be concise and highlight the doctor's expertise and qualifications.")
    result = DataStorage.datastorage.add_doctor(name, password, specialty, email, workplace, degree, summary)
    if not result:
        return f"Doctor {name} already exists!"
    return f"Doctor {name} added successfully!"