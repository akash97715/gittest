import json
import boto3

def lambda_handler(event, context):
    """
    Retrieve documents

    Args:
        event (dict): The current graph state

    Returns:
        dict: New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = event["question"]

    # Retrieval
    documents = retriever.get_relevant_documents(question)
    return {
        "statusCode": 200,
        "body": json.dumps({"documents": documents, "question": question})
    }




import json
import boto3

def lambda_handler(event, context):
    """
    Generate answer

    Args:
        event (dict): The current graph state

    Returns:
        dict: New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = event["question"]
    documents = event["documents"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {
        "statusCode": 200,
        "body": json.dumps({"documents": documents, "question": question, "generation": generation})
    }







import json
import boto3

def lambda_handler(event, context):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        event (dict): The current graph state

    Returns:
        dict: Updates documents key with only filtered relevant documents
    """
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = event["question"]
    documents = event["documents"]

    # Score each doc
    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke({"question": question, "document": d["page_content"]})
        grade = score["binary_score"]
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {
        "statusCode": 200,
        "body": json.dumps({"documents": filtered_docs, "question": question})
    }






import json
import boto3

def lambda_handler(event, context):
    """
    Transform the query to produce a better question.

    Args:
        event (dict): The current graph state

    Returns:
        dict: Updates question key with a re-phrased question
    """
    print("---TRANSFORM QUERY---")
    question = event["question"]
    documents = event["documents"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    return {
        "statusCode": 200,
        "body": json.dumps({"documents": documents, "question": better_question})
    }







import json
import boto3

def lambda_handler(event, context):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        event (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """
    print("---ASSESS GRADED DOCUMENTS---")
    question = event["question"]
    filtered_documents = event["documents"]

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---")
        next_node = "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        next_node = "generate"
    
    return {
        "statusCode": 200,
        "body": json.dumps({"next_node": next_node})
    }






import json
import boto3

def lambda_handler(event, context):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        event (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """
    print("---CHECK HALLUCINATIONS---")
    question = event["question"]
    documents = event["documents"]
    generation = event["generation"]

    score = hallucination_grader.invoke({"documents": documents, "generation": generation})
    grade = score["binary_score"]

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score["binary_score"]
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            next_node = "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            next_node = "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        next_node = "not supported"
    
    return {
        "statusCode": 200,
        "body": json.dumps({"next_node": next_node})
    }





