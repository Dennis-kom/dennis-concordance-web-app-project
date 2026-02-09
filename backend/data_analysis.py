from typing import List, Tuple
from backend.process_maneger import linking_words

def tokenize_text_content (file_content: str) -> Tuple[List[str], List[List[int, str, int, int, int, int]]]:
    # (text_id, token, page_number, line_number, token_index,tag_id)
    content_vector = []
    tokens_data_dump = []
    tokens_list = []
    line_index: int = 0
    token_index: int = 0
    if file_content:
        lines = file_content.split('\n')
        for line in lines:
            line_index += 1
            token_index = 0
            content_vector.extend(line.split(' '))
        for token in content_vector:
            token_index += 1
            if token not in linking_words and token != '':
                tokens_list.append(token)
                tokens_data_dump.append([0, token, 0, line_index, token_index, 0])
    return tokens_list, tokens_data_dump

def grab_lines_with_tokens(token,text_id, line_index, token_index, content):
    lines = content.split('\n')
    grab_result = []
    if token in lines[line_index]:
        grab_result.append(lines[line_index])

    return grab_result



def generate_tag_deriving_matrix():
    ...

def derive_tag_from_tokens_vector(mat, vec: List[str]):
    ...



