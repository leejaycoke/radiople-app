from flask import request


def get_uri(index):
    paths = [p for p in request.path.split('/') if p != '']
    return paths[index] if len(paths) > 0 else None


def allowed_file(filename, allowed_set):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_set
