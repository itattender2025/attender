from pymongo import MongoClient
from datetime import datetime
import os
# from dotenv import load_dotenv

# load_dotenv()

def get_db_connection():
    """Establish connection to MongoDB Atlas"""
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        # Verify connection works
        client.admin.command('ping')
        return client['attender_db']
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

def get_all_student_collections(db):
    """Get all collections starting with 'student_it_'"""
    return [col for col in db.list_collection_names() if col.startswith('student_it_')]

def create_new_collection(db, source_collection, new_collection_name, subjects):
    """Create new collection with promoted students"""
    try:
        source_col = db[source_collection]
        target_col = db[new_collection_name]
        
        students = list(source_col.find())
        
        if not students:
            raise ValueError(f"No students found in collection {source_collection}")
        
        for student in students:
            # Validate required fields exist
            if not all(field in student for field in ['name', 'roll_number']):
                print(f"Skipping invalid student document: {student}")
                continue
            
            new_student = {
                'name': student.get('name', ''),
                'roll_number': student.get('roll_number', ''),
                'current_semester': new_collection_name.split('_')[-2].replace('sem', ''),
                'academic_year': new_collection_name.split('_')[-1],
                'subjects': {subject: {} for subject in subjects},
                'promoted_from': {
                    'source_collection': source_collection,
                    'promotion_date': datetime.now().isoformat(),
                    'original_data': {k: v for k, v in student.items() if k not in ['_id', 'subjects']}
                }
            }
            target_col.insert_one(new_student)
        
        return len(students)
    
    except Exception as e:
        print(f"Error in create_new_collection: {e}")
        raise