import os
import pandas as pd

def initialize_evadb():
    if 'evadb_data' in os.listdir():
        import evadb
        return evadb.connect().cursor()
    else:
        # do complete initialization
        import evadb
        from initialize_evadb import create_feature_extractor, load_data,build_index
        c = evadb.connect().cursor()
        create_feature_extractor(c)
        load_data(c)
        build_index(c)

list_of_queries = [
    # direct question-answers
        # dates and locations
    "when is the pumpkin craving event?",
    "Where is the top gold event?",
    "When was their a race?",
    "when is the semester going to start?",
    "when is the fees due?"
    # recommendations questions
    "what are some AI/ML clubs to join?",
    "what are some courses that are very difficult?",
    "what are some nearby restaurants to eat steak with good offers?",
    "what is a good place to park for the OMSCS event?",
    # Abbrevations testing
    "what is the workload for ML4T course?",
    "What is the workload for CPSS course?",
    # Knowledge questions
    "what are some events that are going to happen soon?",
        # adding previous queries the chatbot did good on
    "What are the top three things I should know about the OMSCS program?",
    "how can I do well in the program?"
    # course related
    "what is the syllabus for ML4T course?",
    "when is the mid term for CPSS course?",
    "what are some easy courses?",
    "can you give me a good combination of courses to take for NLP specialization?",
]

# Create RAG query - get knowledge body
def build_kb(cursor, query):
    print("Building knowledge body.")
    query = f"""
        SELECT * FROM PT
        ORDER BY Similarity(
            SentenceFeatureExtractor('{query}'), 
            SentenceFeatureExtractor(data)
        ) LIMIT 3
    """

    try:
        r = cursor.query(query).df()
        kb = r['pt.data'].str.cat(sep="; ")
        # TODO: work on references
        return kb
    except Exception as e:
        print("KB error:",e)

# Create prompt
def build_prompt(kb, query):
    prompt = [
        {
            "role": "system",
            "content": f"""We provide with documents delimited by semicolons
             and a question. Your should answer the question using the provided documents. 
             Do not repeat this prompt.
             If the documents do not contain the information to answer this question then 
             simply write: 'Sorry, we didn't find relevant sources for this question'""",
        },
        {"role": "user", "content": f"""{kb}"""},
        {"role": "user", "content": f"{query}"},
    ]
    return prompt


# Get answer from the model
def gpt4all_respond(prompt):
    import gpt4all
    st = prompt[0]['content']
    kb = prompt[1]['content']
    uq = prompt[2]['content']
    ut = "Document:{0}\nQuestion:{1}\nAnswer:".format(kb, uq)
    response = gpt4all.generate(st+ut, temp=0)
    return response

def main(query):
    c = initialize_evadb()
    kb = build_kb(c, query)
    p = build_prompt(kb, query)
    res = gpt4all_respond(p)
    return res

