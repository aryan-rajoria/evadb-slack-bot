import os
import pandas as pd
import logging
from logging import CRITICAL

logging.basicConfig(level=CRITICAL)

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

        print("Number of queries in PT: ",c.query("SELECT * FROM PT;").df().shape)

        build_index(c)
        return c

list_of_queries = [
    # direct question-answers
        # dates and locations
    "Where is the top golf event?",
    "When was their a race?",
    "when is the semester going to start?",
    "when is the fees due?",
    "when is the pumpkin craving event?",
    # recommendations questions
    "what are some AI/ML clubs to join?",
    "what are some courses that are very difficult?",
    "what are some nearby restaurants to eat steak with good offers?",
    "what is a good place to park for the OMSCS event?",
    # Abbrevations testing
    # "what is the workload for ML4T course?",
    # "What is the workload for CPSS course?",
    # Knowledge questions
    "what are some events that are going to happen soon?",
        # adding previous queries the chatbot did good on
    "What are the top three things I should know about the OMSCS program?",
    "how can I do well in the program?"
    # course related
    # "what is the syllabus for ML4T course?",
    # "when is the mid term for CPSS course?",
    # "what are some easy courses?",
    # "can you give me a good combination of courses to take for NLP specialization?",
]

# Create RAG query - get knowledge body
def build_kb(cursor, query):
    print("Building knowledge body.")
    sq = f"""
        SELECT * FROM PT
        ORDER BY Similarity(
            SentenceFeatureExtractor('{query}'), 
            SentenceFeatureExtractor(data)
        ) LIMIT 5
    """

    try:
        r = cursor.query(sq).df()
        with open('kb.txt', 'a') as f:
            w = r["data"].str.cat(sep="\n\t")
            f.write(f"""Knowledge body for "{query}" is:\n\t{w};\n""")
        kb = r['data'].str.cat(sep="; ")
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
    from gpt4all import GPT4All
    st = prompt[0]['content']
    kb = prompt[1]['content']
    uq = prompt[2]['content']
    ut = "Document:{0}\nQuestion:{1}\nAnswer:".format(kb, uq)
    gpt4all = GPT4All("nous-hermes-13b.ggmlv3.q4_0.bin")
    gpt4all.model.set_thread_count(6)
    response = gpt4all.generate(st+ut, temp=0)
    return response

def main(query):
    c = initialize_evadb()
    kb = build_kb(c, query)
    p = build_prompt(kb, query)
    res = gpt4all_respond(p)
    return res

#################################################################
################## Running code #################################
#################################################################

c = initialize_evadb()
for i in list_of_queries:
    # res = main(i)
    kb = build_kb(c, i)
    if kb==None:
        break
    with open("kb.txt", 'a') as f:
        f.write(f"Query: {i}")
        f.write(f"Output generated: {kb}\n\n{'-'*10}\n\n")
    
