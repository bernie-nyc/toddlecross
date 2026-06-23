from .toddle_client import ToddleClient
from .veracross_client import VeracrossClient

# This class runs the sync process. It reads data from Veracross,
# maps it to the Toddle format, figures out what changed, and updates Toddle.
class SyncPipeline:
    # This initializer creates the API clients we need for both websites.
    def __init__(self):
        # We create a client to talk to the Toddle app.
        self.toddle_client = ToddleClient()
        # We create a client to talk to the Veracross school system.
        self.veracross_client = VeracrossClient()

    # This method takes a student dictionary from Veracross
    # and translates its keys to match what Toddle expects.
    def map_student(self, veracross_student):
        # We extract fields and map them to a clean dictionary structure.
        return {
            'sis_id': str(veracross_student.get('student_id', veracross_student.get('id', ''))),
            'first_name': veracross_student.get('first_name', ''),
            'last_name': veracross_student.get('last_name', ''),
            'email': veracross_student.get('email', '').strip().lower(),
            'grade': veracross_student.get('grade_level', '')
        }

    # This method takes a teacher dictionary from Veracross
    # and translates its keys to match what Toddle expects.
    def map_teacher(self, veracross_teacher):
        return {
            'sis_id': str(veracross_teacher.get('teacher_id', veracross_teacher.get('id', ''))),
            'first_name': veracross_teacher.get('first_name', ''),
            'last_name': veracross_teacher.get('last_name', ''),
            'email': veracross_teacher.get('email', '').strip().lower()
        }

    # This method compares two list of users to find additions, edits, and deletions.
    # It returns a dictionary specifying what needs to be created, updated, or removed.
    def calculate_diff(self, existing_toddle_users, incoming_veracross_users, id_field='email'):
        # We group existing Toddle users by their email or ID for fast lookup.
        existing_lookup = {
            user.get(id_field): user 
            for user in existing_toddle_users 
            if user.get(id_field)
        }
        
        # We group incoming Veracross users by the same key.
        incoming_lookup = {
            user.get(id_field): user 
            for user in incoming_veracross_users 
            if user.get(id_field)
        }

        to_create = []
        to_update = []
        to_delete = []

        # Find users that are new or need updating.
        for key, incoming_user in incoming_lookup.items():
            if key not in existing_lookup:
                # If they do not exist in Toddle, we must create them.
                to_create.append(incoming_user)
            else:
                # If they do exist, we compare their properties to see if any field has changed.
                existing_user = existing_lookup[key]
                has_changed = False
                for field in incoming_user:
                    # We check if the incoming value differs from the existing value.
                    if incoming_user[field] != existing_user.get(field):
                        has_changed = True
                        break
                if has_changed:
                    # If fields are different, we add them to the update list.
                    to_update.append(incoming_user)

        # Find users that are in Toddle but no longer exist in Veracross.
        for key, existing_user in existing_lookup.items():
            if key not in incoming_lookup:
                # If they are missing in the new data, we must remove them.
                to_delete.append(existing_user)

        return {
            'to_create': to_create,
            'to_update': to_update,
            'to_delete': to_delete
        }

    # This method executes the full sync workflow for students.
    def sync_students(self):
        # 1. Fetch student data from Veracross REST API.
        veracross_raw = self.veracross_client.get_students()
        
        # 2. Map Veracross data to Toddle schema.
        mapped_incoming = [self.map_student(student) for student in veracross_raw]

        # 3. Fetch existing students from Toddle using a GraphQL query.
        query = """
        query GetExistingStudents {
            students {
                sis_id
                first_name
                last_name
                email
                grade
            }
        }
        """
        try:
            # We fetch existing student records from the Toddle server.
            toddle_response = self.toddle_client.execute_graphql(query)
            existing_students = toddle_response.get('data', {}).get('students', [])
        except Exception:
            # Fall back to empty list if query fails or server is not initialized.
            existing_students = []

        # 4. Calculate what records need to be added, changed, or deleted.
        diff = self.calculate_diff(existing_students, mapped_incoming)

        # 5. Push changes to Toddle using GraphQL mutations.
        results = {
            'created_count': 0,
            'updated_count': 0,
            'deleted_count': 0
        }

        # Handle student creations.
        create_mutation = """
        mutation CreateStudent($input: StudentInput!) {
            createStudent(input: $input) {
                sis_id
            }
        }
        """
        for student in diff['to_create']:
            try:
                self.toddle_client.execute_graphql(create_mutation, {'input': student})
                results['created_count'] += 1
            except Exception:
                pass

        # Handle student updates.
        update_mutation = """
        mutation UpdateStudent($input: StudentInput!) {
            updateStudent(input: $input) {
                sis_id
            }
        }
        """
        for student in diff['to_update']:
            try:
                self.toddle_client.execute_graphql(update_mutation, {'input': student})
                results['updated_count'] += 1
            except Exception:
                pass

        # Handle student deletions.
        delete_mutation = """
        mutation DeleteStudent($email: String!) {
            deleteStudent(email: $email) {
                success
            }
        }
        """
        for student in diff['to_delete']:
            try:
                self.toddle_client.execute_graphql(delete_mutation, {'email': student.get('email', '')})
                results['deleted_count'] += 1
            except Exception:
                pass

        return results
