# Ensure project root is on sys.path so top-level imports like `data_models` work when
# running this script directly from the `backend` folder.
import os
import sys

# Add project root to sys.path BEFORE any imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import List
from process_maneger import DataStack, linking_words
from data_models.database import OrcaleDatabase
from flask import Flask, render_template, jsonify, request, redirect, url_for
from data_analysis import tokenize_text_content, grab_lines_with_tokens

stack = DataStack.stack

project_root = os.path.dirname(os.path.dirname(__file__))
_frontend_candidate = os.path.join(project_root, "fromtend")
if os.path.isdir(_frontend_candidate):
    frontend_dir = _frontend_candidate
else:
    frontend_dir = os.path.join(project_root, "frontend")

template_folder = os.path.join(frontend_dir, "templates")
static_folder = os.path.join(frontend_dir, "static")

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

# Initialize database with proper error handling and logging
db = None
try:
    db = OrcaleDatabase()
    if db.connection:
        print("[OK] Database connection established successfully")
    else:
        print(f"[ERROR] Database connection failed: {db._connect_error}")
except Exception as e:
    print(f"[ERROR] Failed to initialize OrcaleDatabase: {e}")


def data_preload():

    if not db:
        print("Skipping data_preload: database not available")
    try:
        db.preload_base_models()
    except Exception as e:
        print(f"Warning: data_preload failed: {e}")


# Define routes before calling `app.run` so they're registered correctly.
@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    stack['topics'] = []
    stack['results'] = []

    if db:
        try:
            data_preload()
            stack['topics'] = db.get_tags_list() or []
            print(f"Loaded {stack['topics']} topics from database")
        except Exception as e:
            # If any DB error happens, fall back to empty list and log a warning.
            print(f"Warning: failed to get tags list: {e}")

    return render_template("index.html", topics=stack['topics'], result_lines=stack['results'])

@app.route("/submit", methods=["POST"])
def submit():
    # Handle JSON requests (user text submission with all field data)
    if request.is_json:
        try:
            data = request.get_json()
            user_input = data.get('user_input', '').strip()
            selected_tags = data.get('selected_tags', [])
            uploaded_files = data.get('uploaded_files', [])
            text_window_content = data.get('text_window_content', '')
            timestamp = data.get('timestamp', '')

            print(f"\n{'='*60}")
            print(f"RECEIVED ALL FORM DATA:")
            print(f"{'='*60}")
            print(f"User Input: {user_input}")
            print(f"Selected Tags: {selected_tags}")
            print(f"Uploaded Files: {len(uploaded_files)} file(s)")
            for f in uploaded_files:
                print(f"  - {f['name']} ({f['size']} bytes, type: {f['type']})")
                print(f"    Content preview: {f['content'][:100]}...")
            print(f"Text Window Content Length: {len(text_window_content)} characters")
            print(f"Timestamp: {timestamp}")
            print(f"{'='*60}\n")

            if not user_input and not uploaded_files:
                return jsonify({'success': False, 'error': 'Please provide text or upload files'}), 400

            if db and db.connection:
                # TODO: Process the submitted data
                print(f"Processing submitted data with {len(selected_tags)} tags")

                # Process uploaded files with their content
                for file_data in uploaded_files:
                    try:
                        filename = file_data['name']
                        content = file_data['content']
                        suspected_tag = "Unknown"
                        print(f"\n>>> Processing file: {filename}")
                        print(f"    Content length: {len(content)} characters")

                        # all the tokens that derived from current text file
                        file_tokens, tokens_table_dump = tokenize_text_content(content)
                        print(f"    Extracted {len(file_tokens)} tokens")

                        # according to the tokens attemt to derive what tag (topic) is most acceptable to this text
                        # form database root token table - create a matrix for analising the new tokens
                        # tokens, topic (tag)
                        root_tag_matrix = db.generate_tokens_root_vector()  # list of tuples (token, tag)
                        print(f"    Retrieved {len(root_tag_matrix)} root tokens from database for analysis")
                        print(f"    Sample root tokens: {root_tag_matrix[:5]}")
                        root_token_histegram = {}
                        topic_histegram = {}
                        for token, tag in root_tag_matrix:
                            root_token_histegram[token] = tag
                            # filling the topic (tag) histegram - it will be used to define the tag of the new file
                            if tag not in topic_histegram:
                                topic_histegram[tag] = 0

                        # try to find the new tokens in the root tokens
                        token_histegram = dict.fromkeys(file_tokens, 0)
                        print(f"    Initialized token histogram for file tokens with {len(token_histegram)} entries")
                        for token in token_histegram.keys():
                            print(f"    Analyzing token: '{token}'")
                            token_raw = token.strip().lower()
                            token_upper = token.strip().upper()
                            token_capitalized = token.strip().capitalize()
                            if (token_raw in root_token_histegram.keys() or
                                    token in root_token_histegram.keys() or
                                    token_upper in root_token_histegram.keys() or
                                    token_capitalized in root_token_histegram.keys()):

                                if root_token_histegram.get(token_raw):
                                    token_histegram[token] = root_token_histegram[token_raw] # assign the tag from root tokens
                                    topic_histegram[root_token_histegram[token_raw]] += 1 # increment the count for this tag in the topic histogram
                                elif root_token_histegram.get(token):
                                    token_histegram[token] = root_token_histegram[token] # assign the tag from root tokens
                                    topic_histegram[root_token_histegram[token]] += 1 # increment the count for this tag in the topic histogram
                                elif root_token_histegram.get(token_upper):
                                    token_histegram[token] = root_token_histegram[token_upper] # assign the tag from root tokens
                                    topic_histegram[root_token_histegram[token_upper]] += 1 # increment the count for this tag in the topic histogram
                                elif root_token_histegram.get(token_capitalized):
                                    token_histegram[token] = root_token_histegram[token_capitalized] # assign the tag from root tokens
                                    topic_histegram[root_token_histegram[token_capitalized]] += 1 # increment the count for this tag in the topic histogram
                            else:
                                token_histegram[token] = "Unknown"  # not found in root tokens

                        # if the token intersection is partial like 33% than the tag is the tag of the intersection
                        suspected_tag = None
                        if topic_histegram:
                            suspected_tag = max(topic_histegram, key=topic_histegram.get)
                            print(f"    Topic histogram: {topic_histegram}")
                            print(f"    Suspected tag based on histogram: '{suspected_tag}' with {topic_histegram[suspected_tag]} matches")
                        if len(file_tokens) > 0 and suspected_tag and topic_histegram[suspected_tag] / sum(topic_histegram.values()) >= 0.33:
                            print(f"    [OK] Classified under tag '{suspected_tag}' with {topic_histegram[suspected_tag]} matching tokens out of {len(file_tokens)} total")

                        else:
                            suspected_tag = "Unknown"
                            print(f"    [WARN] Classified as 'Unknown' - low confidence match")

                            print(f"insertng into text table unknown tag")

                            if suspected_tag is None or suspected_tag == "Unknown":
                                # TODO: - give to this table temporary tag name - will be defined later
                                # TODO: - if no tag matched then it should be a new tag - in this case create a new table of a new tag
                                ...
                                # TODO: need to create new tag
                                # TODO: - insert the tokens of the unknown topic as a new tag
                            try:
                                suspected_tag_id = db.get_tag_id_by_name(suspected_tag)
                                db.insert_into_text_table(suspected_tag_id, filename, content)
                                # insert the tokens into tokens tabe with the tag id - it will be used later to define the tag of the new files
                                for token in file_tokens:
                                    for tup in tokens_table_dump:
                                        try:
                                            tup[0] = db.find_text_id_by_name(filename)
                                            tup[5] = suspected_tag_id
                                            # TODO: need to implemnt with db gasp only
                                            stack['results'].append(grab_lines_with_tokens(token, tup[0], tup[3],tup[4], content))
                                        except Exception as e:
                                            print(f"Error finding text ID for file '{filename}': {e}")
                                    try:
                                        db.insert_into_tokens_table(tokens_table_dump)

                                    except Exception as e:
                                        print(f"Error inserting tokens for file '{filename}' into tokens table: {e}")
                            except Exception as e:
                                print(f"Error inserting file '{filename}' into text table with tag '{suspected_tag}': {e}")


                    except Exception as e:
                        print(f"Error processing file {filename}: {e}")
                        import traceback
                        traceback.print_exc()

                # Example: tokenize the user input if provided
                if user_input:
                    tokens, tokens_table_dump = tokenize_text_content(user_input)
                    print(f"Extracted {len(tokens)} tokens from user input")

            return jsonify({
                'success': True,
                'message': f'Successfully received and processed all data',
                'data_received': {
                    'user_input': user_input,
                    'tags_count': len(selected_tags),
                    'files_count': len(uploaded_files),
                    'content_length': len(text_window_content)
                }
            }), 200

        except Exception as e:
            print(f"Error in /submit (JSON): {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500


    # return redirect(url_for('index'))


@app.route("/health/db")
def health_db():
    """Return a small JSON object describing database availability and basic health info.
    - available: True/False whether a DB connection is present
    - connect_error: text of any connect error captured during OrcaleDatabase construction
    - tags_count: number of rows in the tags table (if accessible)
    """

    if db is None:
        return jsonify({"available": False, "error": "Database helper not available"}), 503

    # If OrcaleDatabase exists but couldn't connect, report the connect error
    if not getattr(db, 'connection', None):
        return jsonify({"available": False, "connect_error": getattr(db, '_connect_error', 'No connection info')}), 503

    # Try a lightweight query to check DB responsiveness and get a tags count
    try:
        with db.connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM tags")
            row = cur.fetchone()
            tags_count = int(row[0]) if row and row[0] is not None else 0
    except Exception as e:
        # The DB is reachable but the query failed (e.g., table doesn't exist)
        return jsonify({"available": True, "error": str(e)}), 200

    return jsonify({"available": True, "tags_count": tags_count}), 200


if __name__ == "__main__":
    # When running locally it's helpful to see which folders are being used.
    print(f"Using templates: {template_folder}")
    print(f"Using static: {static_folder}")
    app.run(host='127.0.0.1', debug=True)
