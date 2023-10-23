import os
import pandas as pd
import torch
import pickle

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
        return c

list_of_queries = [
    # direct question-answers
        # dates and locations
    "when is the pumpkin craving event?",
    "Where is the top gold event?",
    # "When was their a race?",
    # "when is the semester going to start?",
    "when is the fees due?"
    # recommendations questions
    "what are some AI/ML clubs to join?",
    "what are some courses that are very difficult?",
    "what are some nearby restaurants to eat steak with good offers?",
    "what is a good place to park for the OMSCS event?",
    # Abbrevations testing
    # "what is the workload for ML4T course?",
    "What is the workload for CPSS course?",
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
class Knowledge_Builder:
    def __init__(self, cursor, query):
        print("Building knowledge body.")
        query = f"""
            SELECT * FROM PT
            ORDER BY Similarity(
                SentenceFeatureExtractor('{query}'), 
                SentenceFeatureExtractor(data)
            );
        """
        self.kb = None
        self.start = 0
        self.end = 5
        try:
            r = cursor.query(query).df()
            self.kb = r
        except Exception as e:
            print("KB error:",e)
    
    def give_kb(self):
        r = self.kb.loc[self.start:self.end, ('data')].str.cat(sep="; ")
        return r

    def initial_kb(self):
        r = self.kb.loc[0:5, ('data')].str.cat(sep="; ")
        return r

    def compute_next_kb(self):
        self.start = self.end
        self.end = self.end+5


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

from gpt4all import GPT4All
gpt4all = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf", model_path="/home/great/.cache/gpt4all/", device='gpu')

def get_oracle_response(kb, query):
    sp = "system\n-If the knowledge body is sufficient to answer the query say Yes else say No."
    kp = f"Knowledge body - {kb}"
    qp = f"query - {query}"
    pt="{0}"
    r = ''
    with gpt4all.chat_session(sp, pt):
        r = gpt4all.generate(prompt=kp+qp, temp=0)
    print(f'\nResponse is:\n{r}\n')
    if 'No' in r:
        return True    
    else:
        return False


c = initialize_evadb()
prompts = {}
for query in list_of_queries:
    kb_obj = Knowledge_Builder(c,query)

    kb = kb_obj.give_kb()
    print(f"\n\n{kb}\n\n")
    count=0
    while(get_oracle_response(kb, query)):
        print("\n\nKnowledge body not good\n\n")
        kb_obj.compute_next_kb()
        kb = kb_obj.give_kb()
        count+=1
        if count>3:
            print("\n\nNone of the KBs were good\n\n")
            kb = kb_obj.initial_kb()
            break

    p = build_prompt(kb, query)
    prompts[query]=p
print(prompts)

with open('prompt.pkl','wb') as fp:
    pickle.dump(prompts, fp)

# prompt={}
# with open('prompt.pkl', 'rb') as fp:
#     prompt = pickle.load(fp)

# from gpt4all import GPT4All
# gpt4all = GPT4All("nous-hermes-13b.ggmlv3.q4_0.bin", device='gpu')

# # Get answer from the model
# def gpt4all_respond(prompt):
#     st = prompt[0]['content']
#     kb = prompt[1]['content']
#     uq = prompt[2]['content']
#     ut = "Document:{0}\nQuestion:{1}\nAnswer:".format(kb, uq)
#     response = gpt4all.generate(st+ut, temp=0)
#     return response

# for query in list_of_queries:
#     res = gpt4all_respond(prompt[query])
#     print("done query:", query)
#     with open('llm.txt', 'a') as f:
#         f.write(f'Prompt is {query}\n')
#         f.write(f"{res}\n")
#         f.write("\n\n")
