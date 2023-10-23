# create featureextractor
def create_feature_extractor(cursor):
    print("Creating Feature Extractor")
    cursor.query(
        """
        CREATE FUNCTION IF NOT EXISTS SentenceFeatureExtractor
        IMPL './sentence_feature_extractor.py'
    """
    ).df()

# load Data into evadb
def load_data(cursor):
    try:
        cursor.query("""LOAD PDF "../../../assets/*.pdf" INTO PT""").df()
    except Exception:
        return False
    return True
# build index
def build_index(cursor):
    print("Building Search Index")
    cursor.query(
        """CREATE INDEX IF NOT EXISTS OMSCSIndex 
        ON PT (SentenceFeatureExtractor(data))
        USING FAISS
    """
    ).df()