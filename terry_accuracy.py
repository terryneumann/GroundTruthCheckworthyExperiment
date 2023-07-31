import json
def truth_evaluation(payload_data_object, gold, annotations, i, max_likert_score=6):

    payload_data_object = payload_data_object.replace('Claim: ', '')
    if payload_data_object in gold:
        content_json = json.loads(annotations[i]['annotationData']['content'])          
        # worker_veracity_score: A dictionary of the form {'1':False, '2':False, ..., '6':True} (for example) from html radio button output.
        worker_veracity_score = content_json['assessment_truth']
        answer = False
        j = 0
        while not answer:
            j += 1
            answer = worker_veracity_score[str(j)] 
        worker_veracity_score = j
        
        if (gold[payload_data_object] == 'Gold_False') and (worker_veracity_score in [max_likert_score - 1, max_likert_score]):
            return 1
        elif (gold[payload_data_object] == 'Gold_True') and (worker_veracity_score in [1, 2]):
            return 1
        else:
            return 0
    else:
        return -1



