from .toddle_client import ToddleClient
from .veracross_client import VeracrossClient

# This class runs the sync process. It reads data from Veracross,
# maps it to the Toddle format, figures out what changed, and updates Toddle.
# It can also accept a SyncJob database object to write logs in real time.
class SyncPipeline:
    # This initializer creates the API clients we need for both websites.
    # It optionally takes a sync_job parameter to write logs to the database.
    def __init__(self, sync_job=None):
        # We create a client to talk to the Toddle app.
        self.toddle_client = ToddleClient()
        # We create a client to talk to the Veracross school system.
        self.veracross_client = VeracrossClient()
        # We save the sync_job database object.
        self.sync_job = sync_job

    # This helper method writes a log message.
    # If a database sync job is present, it saves it there. Otherwise, it prints it.
    def log(self, message):
        if self.sync_job:
            self.sync_job.add_log(message)
        else:
            print(message)

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
        self.log("Sync progress: Initializing student sync pipeline.")
        
        # 1. Fetch student data from Veracross REST API.
        self.log("Sync progress: Requesting student list from Veracross API.")
        veracross_raw = self.veracross_client.get_students()
        self.log(f"Sync progress: Received {len(veracross_raw)} records from Veracross.")
        
        # 2. Map Veracross data to Toddle schema.
        self.log("Sync progress: Mapping Veracross schemas to Toddle standard format.")
        mapped_incoming = [self.map_student(student) for student in veracross_raw]

        # 3. Fetch existing students from Toddle using a GraphQL query.
        self.log("Sync progress: Querying existing students from Toddle GraphQL server.")
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
            self.log(f"Sync progress: Found {len(existing_students)} existing students on Toddle.")
        except Exception as e:
            # Fall back to empty list if query fails or server is not initialized.
            self.log(f"Sync warning: Failed to fetch existing students from Toddle: {e}")
            existing_students = []

        # 4. Calculate what records need to be added, changed, or deleted.
        self.log("Sync progress: Comparing datasets to calculate differences.")
        diff = self.calculate_diff(existing_students, mapped_incoming)
        self.log(f"Sync progress: Diffs computed. Create: {len(diff['to_create'])}, Update: {len(diff['to_update'])}, Delete: {len(diff['to_delete'])}.")

        # 5. Push changes to Toddle using GraphQL mutations.
        results = {
            'created_count': 0,
            'updated_count': 0,
            'deleted_count': 0
        }

        # Handle student creations.
        if diff['to_create']:
            self.log(f"Sync progress: Preprocessing {len(diff['to_create'])} student creations on Toddle.")
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
            except Exception as e:
                self.log(f"Sync error: Failed to create student {student.get('email')}: {e}")

        # Handle student updates.
        if diff['to_update']:
            self.log(f"Sync progress: Preprocessing {len(diff['to_update'])} student updates on Toddle.")
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
            except Exception as e:
                self.log(f"Sync error: Failed to update student {student.get('email')}: {e}")

        # Handle student deletions.
        if diff['to_delete']:
            self.log(f"Sync progress: Preprocessing {len(diff['to_delete'])} student deletions on Toddle.")
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
            except Exception as e:
                self.log(f"Sync error: Failed to delete student {student.get('email')}: {e}")

        # If a sync_job is present, we save the counts directly to the database object.
        if self.sync_job:
            self.sync_job.created_count = (self.sync_job.created_count or 0) + results['created_count']
            self.sync_job.updated_count = (self.sync_job.updated_count or 0) + results['updated_count']
            self.sync_job.deleted_count = (self.sync_job.deleted_count or 0) + results['deleted_count']
            self.sync_job.save()

        self.log("Sync progress: Student sync completed successfully.")
        return results

    # This method executes the full sync workflow for teachers.
    def sync_teachers(self):
        self.log("Sync progress: Initializing teacher sync pipeline.")
        
        # 1. Fetch teacher data from Veracross REST API.
        self.log("Sync progress: Requesting teacher list from Veracross API.")
        veracross_raw = self.veracross_client.get_teachers()
        self.log(f"Sync progress: Received {len(veracross_raw)} records from Veracross.")
        
        # 2. Map Veracross data to Toddle schema.
        self.log("Sync progress: Mapping Veracross schemas to Toddle standard format.")
        mapped_incoming = [self.map_teacher(teacher) for teacher in veracross_raw]

        # 3. Fetch existing teachers from Toddle using a GraphQL query.
        self.log("Sync progress: Querying existing teachers from Toddle GraphQL server.")
        query = """
        query GetExistingTeachers {
            teachers {
                sis_id
                first_name
                last_name
                email
            }
        }
        """
        try:
            # We fetch existing teacher records from the Toddle server.
            toddle_response = self.toddle_client.execute_graphql(query)
            existing_teachers = toddle_response.get('data', {}).get('teachers', [])
            self.log(f"Sync progress: Found {len(existing_teachers)} existing teachers on Toddle.")
        except Exception as e:
            # Fall back to empty list if query fails or server is not initialized.
            self.log(f"Sync warning: Failed to fetch existing teachers from Toddle: {e}")
            existing_teachers = []

        # 4. Calculate what records need to be added, changed, or deleted.
        self.log("Sync progress: Comparing datasets to calculate differences.")
        diff = self.calculate_diff(existing_teachers, mapped_incoming)
        self.log(f"Sync progress: Diffs computed. Create: {len(diff['to_create'])}, Update: {len(diff['to_update'])}, Delete: {len(diff['to_delete'])}.")

        # 5. Push changes to Toddle using GraphQL mutations.
        results = {
            'created_count': 0,
            'updated_count': 0,
            'deleted_count': 0
        }

        # Handle teacher creations.
        if diff['to_create']:
            self.log(f"Sync progress: Preprocessing {len(diff['to_create'])} teacher creations on Toddle.")
        create_mutation = """
        mutation CreateTeacher($input: TeacherInput!) {
            createTeacher(input: $input) {
                sis_id
            }
        }
        """
        for teacher in diff['to_create']:
            try:
                self.toddle_client.execute_graphql(create_mutation, {'input': teacher})
                results['created_count'] += 1
            except Exception as e:
                self.log(f"Sync error: Failed to create teacher {teacher.get('email')}: {e}")

        # Handle teacher updates.
        if diff['to_update']:
            self.log(f"Sync progress: Preprocessing {len(diff['to_update'])} teacher updates on Toddle.")
        update_mutation = """
        mutation UpdateTeacher($input: TeacherInput!) {
            updateTeacher(input: $input) {
                sis_id
            }
        }
        """
        for teacher in diff['to_update']:
            try:
                self.toddle_client.execute_graphql(update_mutation, {'input': teacher})
                results['updated_count'] += 1
            except Exception as e:
                self.log(f"Sync error: Failed to update teacher {teacher.get('email')}: {e}")

        # Handle teacher deletions.
        if diff['to_delete']:
            self.log(f"Sync progress: Preprocessing {len(diff['to_delete'])} teacher deletions on Toddle.")
        delete_mutation = """
        mutation DeleteTeacher($email: String!) {
            deleteTeacher(email: $email) {
                success
            }
        }
        """
        for teacher in diff['to_delete']:
            try:
                self.toddle_client.execute_graphql(delete_mutation, {'email': teacher.get('email', '')})
                results['deleted_count'] += 1
            except Exception as e:
                self.log(f"Sync error: Failed to delete teacher {teacher.get('email')}: {e}")

        # If a sync_job is present, we save the counts directly to the database object.
        if self.sync_job:
            self.sync_job.created_count = (self.sync_job.created_count or 0) + results['created_count']
            self.sync_job.updated_count = (self.sync_job.updated_count or 0) + results['updated_count']
            self.sync_job.deleted_count = (self.sync_job.deleted_count or 0) + results['deleted_count']
            self.sync_job.save()

        self.log("Sync progress: Teacher sync completed successfully.")
        return results
