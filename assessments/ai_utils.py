try:
    import spacy
    # Load the local spaCy model
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None
except ImportError:
    spacy = None
    nlp = None

import random

class MCQGenerator:
    """
    A local MCQ generator that uses spaCy to extract technical keywords 
    from a job description and generate relevant technical questions.
    """
    
    # Local knowledge base for question templates
    # In a real-world scenario, this could be a JSON file or a larger database
    KNOWLEDGE_BASE = {
        "python": [
            {
                "question": "What is the primary use of 'init' in Python classes?",
                "options": ["To initialize a new object", "To delete an object", "To import modules", "To handle exceptions"],
                "answer": "A"
            },
            {
                "question": "Which of these is a mutable data type in Python?",
                "options": ["Tuple", "String", "List", "Integer"],
                "answer": "C"
            }
        ],
        "django": [
            {
                "question": "What is the purpose of Django's 'models.py'?",
                "options": ["To define the UI layout", "To handle URL routing", "To define the database schema", "To manage static files"],
                "answer": "C"
            },
            {
                "question": "Which command is used to create a new database migration in Django?",
                "options": ["python manage.py runserver", "python manage.py makemigrations", "python manage.py migrate", "python manage.py startapp"],
                "answer": "B"
            }
        ],
        "react": [
            {
                "question": "What is a 'Hook' in React?",
                "options": ["A way to use state in functional components", "A CSS styling method", "A tool for database connection", "A type of HTML tag"],
                "answer": "A"
            }
        ],
        "javascript": [
            {
                "question": "What is 'closures' in JavaScript?",
                "options": ["A function inside another function", "A way to close a window", "A method for loop termination", "A type of variable"],
                "answer": "A"
            }
        ],
        "sql": [
            {
                "question": "What does SQL stand for?",
                "options": ["Structured Query Language", "Sequential Query Language", "Standard Query Level", "Simple Query Logic"],
                "answer": "A"
            }
        ],
        "general": [
            {
                "question": "What is the main goal of Version Control Systems like Git?",
                "options": ["To track changes in source code", "To design graphics", "To host websites", "To compile code"],
                "answer": "A"
            }
        ]
    }

    @staticmethod
    def extract_keywords(text):
        if not nlp:
            return ["general"]
        
        doc = nlp(text.lower())
        keywords = []
        
        # Look for technical terms (simple implementation)
        tech_terms = MCQGenerator.KNOWLEDGE_BASE.keys()
        
        for token in doc:
            if token.text in tech_terms:
                keywords.append(token.text)
        
        # Also look for entities if needed
        # for ent in doc.ents:
        #     if ent.label_ in ["ORG", "PRODUCT"]:
        #         keywords.append(ent.text)
                
        return list(set(keywords)) if keywords else ["general"]

    @staticmethod
    def generate_questions(description, count=5):
        keywords = MCQGenerator.extract_keywords(description)
        selected_questions = []
        
        # Flatten available questions based on detected keywords
        pool = []
        for kw in keywords:
            pool.extend(MCQGenerator.KNOWLEDGE_BASE.get(kw, []))
        
        # If pool is too small, add from 'general'
        if len(pool) < count:
            pool.extend(MCQGenerator.KNOWLEDGE_BASE.get("general", []))
            
        # Shuffle and select
        random.shuffle(pool)
        
        # Ensure we have enough unique questions
        unique_pool = []
        seen = set()
        for q in pool:
            if q['question'] not in seen:
                unique_pool.append(q)
                seen.add(q['question'])
        
        return unique_pool[:count]
