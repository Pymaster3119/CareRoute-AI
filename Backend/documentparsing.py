import AIScripts.runVLM
import AIScripts.calcSimilarityScore
import DataStorage.datastorage

def parse_document(document_dir, caption):
    #Create a phrase for the document and caption
    phrase = AIScripts.runVLM.run_vlm("You are an expert at analysing medical documents", f"Please provide a concise summary of the following document with the following caption: {caption}. The summary should be concise and highlight the skills needed from a doctor to interpret it.", document_dir)

    #Loop through doctors and find the best matches
    best_matches = []
    for i in range(DataStorage.datastorage.get_num_doctors()):
        doctor = DataStorage.datastorage.get_doctor_by_id(i + 1)
        similarity_score = AIScripts.calcSimilarityScore.calculate_similarity_score(phrase, doctor[7])
        print(similarity_score)
        best_matches.append((doctor, similarity_score))

    best_matches.sort(key=lambda x: x[1], reverse=True)

    return best_matches