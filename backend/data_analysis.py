from typing import List, Tuple, Any
from backend.process_maneger import linking_words

def tokenize_text_content (file_content: str) -> Tuple[List[str], List[Any]]:
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
                tokens_data_dump.append([0, token, 0, line_index, token_index, 0,0,0,0,0])
    return tokens_list, tokens_data_dump

def grab_lines_with_tokens(token, content):
    lines = content.split('\n')
    grab_result = []
    for line in lines:
        if token in line:
            listed_line = line.split(' ')
            idx = listed_line.index(token)
            i = 0
            for word in listed_line:
                if '.' in word or ',' in word or ';' in word or ':' in word or '!' in word or '?' in word:
                    break
                i += 1

            if idx == 0:
                shrinked_line = " ".join(listed_line[:i])
            elif idx == len(listed_line) - 1:
                shrinked_line = " ".join(listed_line[-3:])
            else:
                shrinked_line = " ".join(listed_line[idx-1:i])

            grab_result.append(f"{shrinked_line}\n")


    return grab_result



def generate_tag_deriving_matrix():
    ...

def derive_tag_from_tokens_vector(mat, vec: List[str]):
    ...



